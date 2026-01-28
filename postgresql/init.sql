-- Create books table
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    novel_title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    publisher VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial data
INSERT INTO books (title, novel_title, author, publisher) VALUES
    ('The Expanse', 'Leviathan Wakes', 'James S. A. Corey', 'Orbit Book'),
    ('The Expanse', 'Caliban''s War', 'James S. A. Corey', 'Orbit Book'),
    ('The Expanse', 'Abaddon''s Gate', 'James S. A. Corey', 'Orbit Book'),
    ('The Expanse', 'Cibola Burn', 'James S. A. Corey', 'Orbit Book'),
    ('The Expanse', 'Nemesis Games', 'James S. A. Corey', 'Orbit Book'),
    ('The Expanse', 'Babylon''s Ashes', 'James S. A. Corey', 'Orbit Book');

-- Create index for faster queries
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
