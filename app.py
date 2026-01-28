from flask import Flask, jsonify, request, render_template, redirect, url_for
from prometheus_client import Counter, Histogram, start_http_server
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# ===== DATABASE CONFIG =====
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'connect_timeout': 5
}

def validate_db_config():
    """Validate required environment variables"""
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        print(error_msg)
        print("\nRequired environment variables:")
        print("  - DB_HOST: PostgreSQL host address")
        print("  - DB_NAME: Database name")
        print("  - DB_USER: Database username")
        print("  - DB_PASSWORD: Database password")
        print("  - DB_PORT: Database port (optional, default: 5432)")
        sys.exit(1)

def wait_for_db(max_retries=30, retry_delay=2):
    """Wait for database to be available"""
    print(f"Waiting for database at {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
    
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print(f"✓ Database connection successful!")
            return True
        except psycopg2.OperationalError as e:
            if attempt < max_retries:
                print(f"⨯ Attempt {attempt}/{max_retries}: Database not ready - {e}")
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"✗ Failed to connect to database after {max_retries} attempts")
                print(f"  Last error: {e}")
                return False
    return False

def get_db_connection(max_retries=3):
    """Create database connection with retry logic"""
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except psycopg2.OperationalError as e:
            if attempt < max_retries:
                print(f"Database connection attempt {attempt} failed, retrying...")
                time.sleep(1)
            else:
                print(f"Database connection error after {max_retries} attempts: {e}")
                return None
        except Exception as e:
            print(f"Unexpected database error: {e}")
            return None
    return None

# ===== METRICS =====
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5)
)

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query latency',
    ['operation'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1)
)

DB_ERRORS_TOTAL = Counter(
    'db_errors_total',
    'Total database errors',
    ['operation']
)

# ===== METRICS HOOK =====
@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    latency = time.time() - request.start_time
    endpoint = request.endpoint or "unknown"

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    HTTP_REQUEST_DURATION.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(latency)

    return response

# ===== ROUTES =====
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/books', methods=['GET'])
def get_books():
    start = time.time()
    conn = get_db_connection()
    if not conn:
        DB_ERRORS_TOTAL.labels(operation='select').inc()
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, title, novel_title, author, publisher FROM books ORDER BY id')
        books = cursor.fetchall()
        cursor.close()
        conn.close()
        
        DB_QUERY_DURATION.labels(operation='select').observe(time.time() - start)
        return jsonify(books)
    except Exception as e:
        DB_ERRORS_TOTAL.labels(operation='select').inc()
        print(f"Error fetching books: {e}")
        return jsonify({"error": "Failed to fetch books"}), 500

@app.route('/books', methods=['POST'])
def create_book():
    start = time.time()
    conn = get_db_connection()
    if not conn:
        DB_ERRORS_TOTAL.labels(operation='insert').inc()
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO books (title, novel_title, author, publisher) 
               VALUES (%s, %s, %s, %s)''',
            (
                request.form['title'],
                request.form['novel_title'],
                request.form['author'],
                request.form['publisher']
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        DB_QUERY_DURATION.labels(operation='insert').observe(time.time() - start)
        return redirect(url_for('home'))
    except Exception as e:
        DB_ERRORS_TOTAL.labels(operation='insert').inc()
        print(f"Error creating book: {e}")
        return jsonify({"error": "Failed to create book"}), 500

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    start = time.time()
    conn = get_db_connection()
    if not conn:
        DB_ERRORS_TOTAL.labels(operation='update').inc()
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get current book data
        cursor.execute('SELECT * FROM books WHERE id = %s', (book_id,))
        book = cursor.fetchone()
        
        if not book:
            cursor.close()
            conn.close()
            return jsonify({"message": "Book not found"}), 404
        
        # Update with new values or keep existing
        cursor.execute(
            '''UPDATE books 
               SET title = %s, novel_title = %s, author = %s, publisher = %s, updated_at = CURRENT_TIMESTAMP
               WHERE id = %s''',
            (
                request.form.get('title', book['title']),
                request.form.get('novel_title', book['novel_title']),
                request.form.get('author', book['author']),
                request.form.get('publisher', book['publisher']),
                book_id
            )
        )
        conn.commit()
        
        # Fetch updated book
        cursor.execute('SELECT id, title, novel_title, author, publisher FROM books WHERE id = %s', (book_id,))
        updated_book = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        DB_QUERY_DURATION.labels(operation='update').observe(time.time() - start)
        return jsonify(updated_book)
    except Exception as e:
        DB_ERRORS_TOTAL.labels(operation='update').inc()
        print(f"Error updating book: {e}")
        return jsonify({"error": "Failed to update book"}), 500

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    start = time.time()
    conn = get_db_connection()
    if not conn:
        DB_ERRORS_TOTAL.labels(operation='delete').inc()
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM books WHERE id = %s RETURNING id', (book_id,))
        deleted = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        DB_QUERY_DURATION.labels(operation='delete').observe(time.time() - start)
        
        if deleted:
            return jsonify({"message": "Book deleted"})
        else:
            return jsonify({"message": "Book not found"}), 404
    except Exception as e:
        DB_ERRORS_TOTAL.labels(operation='delete').inc()
        print(f"Error deleting book: {e}")
        return jsonify({"error": "Failed to delete book"}), 500

if __name__ == '__main__':
    # Validate environment variables
    validate_db_config()
    
    # Wait for database to be ready
    if not wait_for_db():
        print("✗ Cannot start application: Database is not available")
        sys.exit(1)
    
    # Start Prometheus metrics server
    print("Starting Prometheus metrics server on port 9090...")
    start_http_server(9090)
    
    # Start Flask app
    print("Starting Flask application on port 8080...")
    app.run(host='0.0.0.0', port=8080)
