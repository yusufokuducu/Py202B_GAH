import json
import httpx
from typing import List, Optional, Dict, Any


class Book:
    """
    Represents a book with title, author, and ISBN.
    """
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"
    
    def to_dict(self) -> dict:
        """Convert book to dictionary for JSON serialization."""
        return {
            "title": self.title, 
            "author": self.author, 
            "isbn": self.isbn
        }


class Library:
    """
    Manages a collection of books with persistence to JSON file.
    """
    def __init__(self, filename: str = "library.json"):
        self.filename = filename
        self.books = self.load_books()
    
    @staticmethod
    def fetch_book_from_api(isbn: str) -> Optional[Dict[str, Any]]:
        """
        Fetch book information from Open Library API.
        
        Args:
            isbn: The ISBN of the book to fetch
            
        Returns:
            Dictionary with book info or None if not found/error
        """
        try:
            url = f"https://openlibrary.org/isbn/{isbn}.json"
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                response = client.get(url)
                
                if response.status_code == 200:
                    book_data = response.json()
                    
                    # Extract title
                    title = book_data.get('title', 'Unknown Title')
                    
                    # Extract authors - Open Library has different author formats
                    authors = []
                    if 'authors' in book_data:
                        for author_ref in book_data['authors']:
                            if isinstance(author_ref, dict) and 'key' in author_ref:
                                # Fetch author details
                                author_url = f"https://openlibrary.org{author_ref['key']}.json"
                                author_response = client.get(author_url)
                                if author_response.status_code == 200:
                                    author_data = author_response.json()
                                    author_name = author_data.get('name', 'Unknown Author')
                                    authors.append(author_name)
                    
                    # If no authors found, use a default
                    if not authors:
                        authors = ['Unknown Author']
                    
                    return {
                        'title': title,
                        'author': ', '.join(authors),
                        'isbn': isbn
                    }
                    
                elif response.status_code == 404:
                    print(f"Book with ISBN {isbn} not found in Open Library.")
                    return None
                else:
                    print(f"API Error: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            print("Request timed out. Please check your internet connection.")
            return None
        except httpx.RequestError as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def add_book_by_isbn(self, isbn: str) -> bool:
        """
        Add a book to the library using only ISBN (fetch details from API).
        
        Args:
            isbn: The ISBN of the book to add
            
        Returns:
            True if book was added successfully, False otherwise
        """
        # Check if book already exists
        if self.find_book(isbn):
            print(f"Book with ISBN {isbn} already exists in the library!")
            return False
        
        print(f"Fetching book information for ISBN {isbn}...")
        book_data = self.fetch_book_from_api(isbn)
        
        if book_data:
            book = Book(book_data['title'], book_data['author'], book_data['isbn'])
            self.books.append(book)
            self.save_books()
            print(f"Successfully added: {book}")
            return True
        else:
            print("Failed to add book. Please try again or add manually.")
            return False

    def load_books(self) -> List[Book]:
        """Load books from JSON file."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Book(b['title'], b['author'], b['isbn']) for b in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_books(self) -> None:
        """Save books to JSON file."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([book.to_dict() for book in self.books], f, indent=4, ensure_ascii=False)
    
    def add_book(self, book: Book) -> None:
        """Add a book to the library."""
        # Check if book with same ISBN already exists
        if self.find_book(book.isbn):
            print(f"Book with ISBN {book.isbn} already exists!")
            return
        
        self.books.append(book)
        self.save_books()
        print(f"Added: {book}")
    
    def remove_book(self, isbn: str) -> bool:
        """Remove a book by ISBN. Returns True if removed, False if not found."""
        book_to_remove = self.find_book(isbn)
        if book_to_remove:
            self.books.remove(book_to_remove)
            self.save_books()
            print(f"Removed book: {book_to_remove}")
            return True
        else:
            print(f"Book with ISBN {isbn} not found.")
            return False
    
    def find_book(self, isbn: str) -> Optional[Book]:
        """Find a book by ISBN."""
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None
    
    def list_books(self) -> None:
        """List all books in the library."""
        if not self.books:
            print("The library is empty.")
            return
        
        print("\n--- Library Books ---")
        for i, book in enumerate(self.books, 1):
            print(f"{i}. {book}")
        print("--------------------")


def main_menu():
    """Main application menu loop."""
    lib = Library()
    
    while True:
        print("\n=== Library Management System ===")
        print("1. Add book by ISBN (from Open Library API)")
        print("2. Add book manually")
        print("3. Remove a book")
        print("4. List all books")
        print("5. Find a book")
        print("6. Exit")
        print("="*42)
        
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            print("\n--- Add Book by ISBN ---")
            isbn = input("Enter the ISBN: ").strip()
            
            if not isbn:
                print("Error: ISBN is required!")
                continue
                
            lib.add_book_by_isbn(isbn)
            
        elif choice == "2":
            print("\n--- Add Book Manually ---")
            title = input("Enter the title: ").strip()
            author = input("Enter the author: ").strip()
            isbn = input("Enter the ISBN: ").strip()
            
            if not all([title, author, isbn]):
                print("Error: All fields are required!")
                continue
                
            new_book = Book(title, author, isbn)
            lib.add_book(new_book)
            
        elif choice == "3":
            print("\n--- Remove Book ---")
            isbn = input("Enter the ISBN of the book to remove: ").strip()
            if isbn:
                lib.remove_book(isbn)
            else:
                print("Error: ISBN is required!")
                
        elif choice == "4":
            lib.list_books()
            
        elif choice == "5":
            print("\n--- Find Book ---")
            isbn = input("Enter the ISBN to search: ").strip()
            if isbn:
                found_book = lib.find_book(isbn)
                if found_book:
                    print(f"Found: {found_book}")
                else:
                    print(f"Book with ISBN {isbn} not found.")
            else:
                print("Error: ISBN is required!")
                
        elif choice == "6":
            print("Thank you for using Library Management System!")
            break
            
        else:
            print("Invalid choice! Please enter a number between 1-6.")


if __name__ == "__main__":
    print("Welcome to the Library Management System!")
    main_menu()