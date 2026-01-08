from flask import Flask, jsonify, request, render_template, redirect, url_for
from prometheus_client import Counter, Histogram, start_http_server
import time

app = Flask(__name__)

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

# ===== DATA =====
books = [
    {"id": 1, "title": "The Expanse", "novel_title": "Leviathan Wakes", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 2, "title": "The Expanse", "novel_title": "Caliban's War", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 3, "title": "The Expanse", "novel_title": "Abaddon's Gate", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 4, "title": "The Expanse", "novel_title": "Cibola Burn", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 5, "title": "The Expanse", "novel_title": "Nemesis Games", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 6, "title": "The Expanse", "novel_title": "Babylon's Ashes", "author": "James S. A. Corey", "publisher": "Orbit Book"},
]

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
    return jsonify(books)

@app.route('/books', methods=['POST'])
def create_book():
    new_book = {
        'id': len(books) + 1,
        'title': request.form['title'],
        'author': request.form['author'],
        'publisher': request.form['publisher'],
        'novel_title': request.form['novel_title']
    }
    books.append(new_book)
    return redirect(url_for('home'))

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        book.update({
            'title': request.form.get('title', book['title']),
            'novel_title': request.form.get('novel_title', book['novel_title']),
            'author': request.form.get('author', book['author']),
            'publisher': request.form.get('publisher', book['publisher']),
        })
        return jsonify(book)
    return jsonify({"message": "Book not found"}), 404

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        books.remove(book)
        return jsonify({"message": "Book deleted"})
    return jsonify({"message": "Book not found"}), 404

if __name__ == '__main__':
    start_http_server(9090)
    app.run(host='0.0.0.0', port=8080)
