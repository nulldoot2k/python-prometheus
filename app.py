from flask import Flask, jsonify, request, render_template, redirect, url_for
 
from prometheus_client import Counter, start_http_server
 
REQUESTS = Counter('http_request_total',
                   'Total number of requests')
 
app = Flask(__name__)
 
# Sample initial book data
books = [
    {"id": 1, "title": "The Expanse", "novel_title": "Leviathan Wakes", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 2, "title": "The Expanse", "novel_title": "Caliban's War", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 3, "title": "The Expanse", "novel_title": "Abaddon's Gate", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 4, "title": "The Expanse", "novel_title": "Cibola Burn", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 5, "title": "The Expanse", "novel_title": "Nemesis Games", "author": "James S. A. Corey", "publisher": "Orbit Book"},
    {"id": 6, "title": "The Expanse", "novel_title": "Babylon's Ashes", "author": "James S. A. Corey", "publisher": "Orbit Book"},
]
 
# Welcome route for the root URL ("/")
@app.route('/')
def home():
    return render_template('index.html')
 
# Get all books
@app.route('/books', methods=['GET'])
def get_books():
    REQUESTS.inc()
    return jsonify(books)
 
# Create a new book
@app.route('/books', methods=['POST'])
def create_book():
    REQUESTS.inc()
    new_book = {
        'id': len(books) + 1,
        'title': request.form['title'],
        'author': request.form['author'],
        'publisher': request.form['publisher'],
        'novel_title': request.form['novel_title']
    }
    books.append(new_book)
    return redirect(url_for('home'))
 
# Update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    REQUESTS.inc()
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        book['title'] = request.form.get('title', book['title'])
        book['novel_title'] = request.form.get('novel_title', book['novel_title'])
        book['author'] = request.form.get('author', book['author'])
        book['publisher'] = request.form.get('publisher', book['publisher'])
        return jsonify(book)
    return jsonify({"message": "Book not found"}), 404
 
# Delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    REQUESTS.inc()
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        books.remove(book)
        return jsonify({"message": "Book deleted"})
    return jsonify({"message": "Book not found"}), 404
 
if __name__ == '__main__':
    start_http_server(9090)
    app.run(host='0.0.0.0', port=8080)
