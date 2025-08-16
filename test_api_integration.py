import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
from main import Library, Book


class TestAPIIntegration:
    """Test cases for Open Library API integration."""
    
    @pytest.fixture
    def temp_library(self):
        """Create a temporary library for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()
        
        library = Library(temp_file.name)
        yield library
        
        # Cleanup
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
    
    @patch('httpx.Client')
    def test_fetch_book_from_api_success(self, mock_client):
        """Test successful API call to fetch book data."""
        # Mock the API responses
        mock_context = mock_client.return_value.__enter__.return_value
        
        # Mock book data response
        book_response = Mock()
        book_response.status_code = 200
        book_response.json.return_value = {
            'title': '1984',
            'authors': [{'key': '/authors/OL113314A'}]
        }
        
        # Mock author data response
        author_response = Mock()
        author_response.status_code = 200
        author_response.json.return_value = {
            'name': 'George Orwell'
        }
        
        # Configure mock to return different responses for different URLs
        mock_context.get.side_effect = [book_response, author_response]
        
        # Test the method
        result = Library.fetch_book_from_api('978-0-452-28423-4')
        
        assert result is not None
        assert result['title'] == '1984'
        assert result['author'] == 'George Orwell'
        assert result['isbn'] == '978-0-452-28423-4'
    
    @patch('httpx.Client')
    def test_fetch_book_from_api_not_found(self, mock_client):
        """Test API call when book is not found (404)."""
        mock_context = mock_client.return_value.__enter__.return_value
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_context.get.return_value = mock_response
        
        result = Library.fetch_book_from_api('invalid-isbn')
        assert result is None
    
    @patch('httpx.Client')
    def test_fetch_book_from_api_network_error(self, mock_client):
        """Test API call with network error."""
        import httpx
        
        mock_context = mock_client.return_value.__enter__.return_value
        mock_context.get.side_effect = httpx.RequestError("Network error")
        
        result = Library.fetch_book_from_api('978-0-452-28423-4')
        assert result is None
    
    @patch('httpx.Client')
    def test_fetch_book_from_api_timeout(self, mock_client):
        """Test API call with timeout."""
        import httpx
        
        mock_context = mock_client.return_value.__enter__.return_value
        mock_context.get.side_effect = httpx.TimeoutException("Request timed out")
        
        result = Library.fetch_book_from_api('978-0-452-28423-4')
        assert result is None
    
    @patch('httpx.Client')
    def test_add_book_by_isbn_success(self, mock_client, temp_library):
        """Test successfully adding a book by ISBN."""
        # Mock the API responses
        mock_context = mock_client.return_value.__enter__.return_value
        
        book_response = Mock()
        book_response.status_code = 200
        book_response.json.return_value = {
            'title': 'The Great Gatsby',
            'authors': [{'key': '/authors/OL123456A'}]
        }
        
        author_response = Mock()
        author_response.status_code = 200
        author_response.json.return_value = {
            'name': 'F. Scott Fitzgerald'
        }
        
        mock_context.get.side_effect = [book_response, author_response]
        
        # Test adding book by ISBN
        result = temp_library.add_book_by_isbn('978-0-7432-7356-5')
        
        assert result is True
        assert len(temp_library.books) == 1
        assert temp_library.books[0].title == 'The Great Gatsby'
        assert temp_library.books[0].author == 'F. Scott Fitzgerald'
        assert temp_library.books[0].isbn == '978-0-7432-7356-5'
    
    @patch('httpx.Client')
    def test_add_book_by_isbn_already_exists(self, mock_client, temp_library):
        """Test adding a book by ISBN when it already exists."""
        # Add a book first
        existing_book = Book("Existing Book", "Existing Author", "978-0-7432-7356-5")
        temp_library.add_book(existing_book)
        
        # Try to add the same ISBN again
        result = temp_library.add_book_by_isbn('978-0-7432-7356-5')
        
        assert result is False
        assert len(temp_library.books) == 1  # Should not add duplicate
    
    @patch('httpx.Client')
    def test_add_book_by_isbn_api_failure(self, mock_client, temp_library):
        """Test adding a book by ISBN when API fails."""
        mock_context = mock_client.return_value.__enter__.return_value
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_context.get.return_value = mock_response
        
        result = temp_library.add_book_by_isbn('invalid-isbn')
        
        assert result is False
        assert len(temp_library.books) == 0
    
    @patch('httpx.Client')
    def test_fetch_book_with_no_authors(self, mock_client):
        """Test fetching book data when no authors are available."""
        mock_context = mock_client.return_value.__enter__.return_value
        
        book_response = Mock()
        book_response.status_code = 200
        book_response.json.return_value = {
            'title': 'Book Without Authors'
            # No 'authors' field
        }
        
        mock_context.get.return_value = book_response
        
        result = Library.fetch_book_from_api('978-1-234-56789-0')
        
        assert result is not None
        assert result['title'] == 'Book Without Authors'
        assert result['author'] == 'Unknown Author'
        assert result['isbn'] == '978-1-234-56789-0'
    
    @patch('httpx.Client')
    def test_fetch_book_author_api_failure(self, mock_client):
        """Test fetching book when author API call fails."""
        mock_context = mock_client.return_value.__enter__.return_value
        
        book_response = Mock()
        book_response.status_code = 200
        book_response.json.return_value = {
            'title': 'Test Book',
            'authors': [{'key': '/authors/OL123456A'}]
        }
        
        author_response = Mock()
        author_response.status_code = 404  # Author not found
        
        mock_context.get.side_effect = [book_response, author_response]
        
        result = Library.fetch_book_from_api('978-1-234-56789-0')
        
        assert result is not None
        assert result['title'] == 'Test Book'
        assert result['author'] == 'Unknown Author'  # Should fallback to default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])