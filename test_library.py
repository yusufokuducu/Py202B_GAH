import pytest
import json
import os
import tempfile
from main import Book, Library


class TestBook:
    """Test cases for Book class."""
    
    def test_book_creation(self):
        """Test book object creation."""
        book = Book("1984", "George Orwell", "978-0-452-28423-4")
        assert book.title == "1984"
        assert book.author == "George Orwell"
        assert book.isbn == "978-0-452-28423-4"
    
    def test_book_str_representation(self):
        """Test book string representation."""
        book = Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0-7432-7356-5")
        expected = "The Great Gatsby by F. Scott Fitzgerald (ISBN: 978-0-7432-7356-5)"
        assert str(book) == expected
    
    def test_book_to_dict(self):
        """Test book to dictionary conversion."""
        book = Book("To Kill a Mockingbird", "Harper Lee", "978-0-06-112008-4")
        expected_dict = {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee", 
            "isbn": "978-0-06-112008-4"
        }
        assert book.to_dict() == expected_dict


class TestLibrary:
    """Test cases for Library class."""
    
    @pytest.fixture
    def temp_library(self):
        """Create a temporary library for testing."""
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()
        
        library = Library(temp_file.name)
        yield library
        
        # Cleanup: remove temporary file
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
    
    @pytest.fixture
    def sample_books(self):
        """Create sample books for testing."""
        return [
            Book("1984", "George Orwell", "978-0-452-28423-4"),
            Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0-7432-7356-5"),
            Book("To Kill a Mockingbird", "Harper Lee", "978-0-06-112008-4")
        ]
    
    def test_library_initialization(self, temp_library):
        """Test library initialization."""
        assert temp_library.books == []
        assert os.path.exists(temp_library.filename) or not temp_library.books
    
    def test_add_book(self, temp_library, sample_books):
        """Test adding a book to library."""
        book = sample_books[0]
        temp_library.add_book(book)
        
        assert len(temp_library.books) == 1
        assert temp_library.books[0].title == "1984"
        assert temp_library.books[0].author == "George Orwell"
        assert temp_library.books[0].isbn == "978-0-452-28423-4"
    
    def test_add_duplicate_book(self, temp_library, sample_books, capsys):
        """Test adding a book with duplicate ISBN."""
        book = sample_books[0]
        temp_library.add_book(book)
        temp_library.add_book(book)  # Try to add same book again
        
        assert len(temp_library.books) == 1  # Should not add duplicate
        captured = capsys.readouterr()
        assert "already exists" in captured.out
    
    def test_find_book_existing(self, temp_library, sample_books):
        """Test finding an existing book."""
        book = sample_books[0]
        temp_library.add_book(book)
        
        found_book = temp_library.find_book("978-0-452-28423-4")
        assert found_book is not None
        assert found_book.title == "1984"
    
    def test_find_book_nonexistent(self, temp_library):
        """Test finding a non-existent book."""
        found_book = temp_library.find_book("non-existent-isbn")
        assert found_book is None
    
    def test_remove_book_existing(self, temp_library, sample_books):
        """Test removing an existing book."""
        book = sample_books[0]
        temp_library.add_book(book)
        
        result = temp_library.remove_book("978-0-452-28423-4")
        assert result is True
        assert len(temp_library.books) == 0
    
    def test_remove_book_nonexistent(self, temp_library, capsys):
        """Test removing a non-existent book."""
        result = temp_library.remove_book("non-existent-isbn")
        assert result is False
        captured = capsys.readouterr()
        assert "not found" in captured.out
    
    def test_list_books_empty(self, temp_library, capsys):
        """Test listing books when library is empty."""
        temp_library.list_books()
        captured = capsys.readouterr()
        assert "empty" in captured.out
    
    def test_list_books_with_content(self, temp_library, sample_books, capsys):
        """Test listing books when library has content."""
        for book in sample_books[:2]:  # Add first 2 books
            temp_library.add_book(book)
        
        temp_library.list_books()
        captured = capsys.readouterr()
        assert "1984" in captured.out
        assert "The Great Gatsby" in captured.out
        assert "Library Books" in captured.out
    
    def test_save_and_load_books(self, temp_library, sample_books):
        """Test saving and loading books from JSON file."""
        # Add books
        for book in sample_books:
            temp_library.add_book(book)
        
        # Create new library instance with same file
        new_library = Library(temp_library.filename)
        
        # Check if books were loaded correctly
        assert len(new_library.books) == 3
        assert new_library.find_book("978-0-452-28423-4") is not None
        assert new_library.find_book("978-0-7432-7356-5") is not None
        assert new_library.find_book("978-0-06-112008-4") is not None
    
    def test_load_books_invalid_json(self, temp_library):
        """Test loading books from invalid JSON file."""
        # Write invalid JSON to file
        with open(temp_library.filename, 'w') as f:
            f.write("invalid json content")
        
        # Create new library instance
        new_library = Library(temp_library.filename)
        assert new_library.books == []
    
    def test_load_books_nonexistent_file(self):
        """Test loading books from non-existent file."""
        library = Library("non_existent_file.json")
        assert library.books == []
    
    def test_json_persistence_format(self, temp_library, sample_books):
        """Test that JSON file has correct format."""
        book = sample_books[0]
        temp_library.add_book(book)
        
        # Read and verify JSON format
        with open(temp_library.filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['title'] == "1984"
        assert data[0]['author'] == "George Orwell"
        assert data[0]['isbn'] == "978-0-452-28423-4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])