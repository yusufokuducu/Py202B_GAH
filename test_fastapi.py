import pytest
import json
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from api import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def setup_test_library():
    """Setup and cleanup test library file."""
    # Setup: create a temporary file for testing
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_file.close()
    
    # Patch the library to use test file
    with patch('api.library.filename', temp_file.name):
        with patch('api.library.books', []):
            yield temp_file.name
    
    # Cleanup
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


class TestFastAPIEndpoints:
    """Test cases for FastAPI endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Welcome to Library Management API" in response.json()["message"]
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["message"] == "API is healthy"
    
    def test_get_stats(self, client):
        """Test statistics endpoint."""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_books" in data
        assert "library_file" in data
        assert "api_version" in data
    
    def test_get_books_empty(self, client, setup_test_library):
        """Test getting books when library is empty."""
        with patch('api.library.books', []):
            response = client.get("/books")
            assert response.status_code == 200
            assert response.json() == []
    
    def test_get_books_with_content(self, client):
        """Test getting books when library has content."""
        from main import Book
        mock_books = [
            Book("1984", "George Orwell", "978-0-452-28423-4"),
            Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0-7432-7356-5")
        ]
        
        with patch('api.library.books', mock_books):
            response = client.get("/books")
            assert response.status_code == 200
            books = response.json()
            assert len(books) == 2
            assert books[0]["title"] == "1984"
            assert books[1]["title"] == "The Great Gatsby"
    
    def test_get_book_by_isbn_found(self, client):
        """Test getting a specific book by ISBN when it exists."""
        from main import Book
        mock_book = Book("1984", "George Orwell", "978-0-452-28423-4")
        
        with patch('api.library.find_book', return_value=mock_book):
            response = client.get("/books/978-0-452-28423-4")
            assert response.status_code == 200
            book = response.json()
            assert book["title"] == "1984"
            assert book["author"] == "George Orwell"
            assert book["isbn"] == "978-0-452-28423-4"
    
    def test_get_book_by_isbn_not_found(self, client):
        """Test getting a specific book by ISBN when it doesn't exist."""
        with patch('api.library.find_book', return_value=None):
            response = client.get("/books/nonexistent-isbn")
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]
    
    @patch('api.library.fetch_book_from_api')
    @patch('api.library.find_book')
    @patch('api.library.save_books')
    def test_add_book_by_isbn_success(self, mock_save, mock_find, mock_fetch, client):
        """Test successfully adding a book by ISBN."""
        # Mock that book doesn't exist yet
        mock_find.return_value = None
        
        # Mock successful API response
        mock_fetch.return_value = {
            'title': '1984',
            'author': 'George Orwell',
            'isbn': '978-0-452-28423-4'
        }
        
        # Mock the books list
        with patch('api.library.books', []):
            response = client.post("/books", json={"isbn": "978-0-452-28423-4"})
            assert response.status_code == 200
            book = response.json()
            assert book["title"] == "1984"
            assert book["author"] == "George Orwell"
    
    @patch('api.library.find_book')
    def test_add_book_by_isbn_already_exists(self, mock_find, client):
        """Test adding a book by ISBN when it already exists."""
        from main import Book
        mock_book = Book("1984", "George Orwell", "978-0-452-28423-4")
        mock_find.return_value = mock_book
        
        response = client.post("/books", json={"isbn": "978-0-452-28423-4"})
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    @patch('api.library.fetch_book_from_api')
    @patch('api.library.find_book')
    def test_add_book_by_isbn_not_found_in_api(self, mock_find, mock_fetch, client):
        """Test adding a book by ISBN when API doesn't find it."""
        mock_find.return_value = None
        mock_fetch.return_value = None
        
        response = client.post("/books", json={"isbn": "invalid-isbn"})
        assert response.status_code == 404
        assert "not found in Open Library" in response.json()["detail"]
    
    def test_add_book_by_isbn_empty_isbn(self, client):
        """Test adding a book with empty ISBN."""
        response = client.post("/books", json={"isbn": ""})
        assert response.status_code == 400
        assert "ISBN is required" in response.json()["detail"]
    
    @patch('api.library.find_book')
    @patch('api.library.save_books')
    def test_add_book_manually_success(self, mock_save, mock_find, client):
        """Test successfully adding a book manually."""
        mock_find.return_value = None
        
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "978-1-234-56789-0"
        }
        
        with patch('api.library.books', []):
            response = client.post("/books/manual", json=book_data)
            assert response.status_code == 200
            book = response.json()
            assert book["title"] == "Test Book"
            assert book["author"] == "Test Author"
            assert book["isbn"] == "978-1-234-56789-0"
    
    @patch('api.library.find_book')
    def test_add_book_manually_already_exists(self, mock_find, client):
        """Test adding a book manually when it already exists."""
        from main import Book
        mock_book = Book("Test Book", "Test Author", "978-1-234-56789-0")
        mock_find.return_value = mock_book
        
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "978-1-234-56789-0"
        }
        
        response = client.post("/books/manual", json=book_data)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_add_book_manually_missing_fields(self, client):
        """Test adding a book manually with missing fields."""
        book_data = {
            "title": "",
            "author": "Test Author",
            "isbn": "978-1-234-56789-0"
        }
        
        response = client.post("/books/manual", json=book_data)
        assert response.status_code == 400
        assert "required" in response.json()["detail"]
    
    @patch('api.library.find_book')
    @patch('api.library.save_books')
    def test_remove_book_success(self, mock_save, mock_find, client):
        """Test successfully removing a book."""
        from main import Book
        mock_book = Book("1984", "George Orwell", "978-0-452-28423-4")
        mock_find.return_value = mock_book
        
        with patch('api.library.books', [mock_book]):
            response = client.delete("/books/978-0-452-28423-4")
            assert response.status_code == 200
            assert "has been removed" in response.json()["message"]
    
    @patch('api.library.find_book')
    def test_remove_book_not_found(self, mock_find, client):
        """Test removing a book that doesn't exist."""
        mock_find.return_value = None
        
        response = client.delete("/books/nonexistent-isbn")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])