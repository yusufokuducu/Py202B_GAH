from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from main import Library, Book
import os

app = FastAPI(
    title="Library Management API",
    description="A RESTful API for managing a library with Open Library integration",
    version="1.0.0"
)

# Pydantic models for request/response
class BookResponse(BaseModel):
    """Response model for book data."""
    title: str
    author: str
    isbn: str
    
    class Config:
        from_attributes = True

class ISBNRequest(BaseModel):
    """Request model for ISBN input."""
    isbn: str

class BookRequest(BaseModel):
    """Request model for manual book creation."""
    title: str
    author: str
    isbn: str

class MessageResponse(BaseModel):
    """Response model for messages."""
    message: str

# Global library instance
library = Library("api_library.json")

@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint with API information."""
    return MessageResponse(message="Welcome to Library Management API! Visit /docs for interactive documentation.")

@app.get("/books", response_model=List[BookResponse])
async def get_books():
    """
    Get all books in the library.
    
    Returns:
        List of all books in the library
    """
    books = []
    for book in library.books:
        books.append(BookResponse(
            title=book.title,
            author=book.author,
            isbn=book.isbn
        ))
    return books

@app.post("/books", response_model=BookResponse)
async def add_book_by_isbn(isbn_request: ISBNRequest):
    """
    Add a book to the library using ISBN (fetches data from Open Library API).
    
    Args:
        isbn_request: Request containing the ISBN
        
    Returns:
        The added book information
        
    Raises:
        HTTPException: If book already exists, ISBN is invalid, or API fails
    """
    isbn = isbn_request.isbn.strip()
    
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN is required")
    
    # Check if book already exists
    if library.find_book(isbn):
        raise HTTPException(status_code=409, detail=f"Book with ISBN {isbn} already exists")
    
    # Try to fetch from API and add book
    book_data = library.fetch_book_from_api(isbn)
    
    if book_data:
        book = Book(book_data['title'], book_data['author'], book_data['isbn'])
        library.books.append(book)
        library.save_books()
        
        return BookResponse(
            title=book.title,
            author=book.author,
            isbn=book.isbn
        )
    else:
        raise HTTPException(status_code=404, detail=f"Book with ISBN {isbn} not found in Open Library")

@app.post("/books/manual", response_model=BookResponse)
async def add_book_manually(book_request: BookRequest):
    """
    Add a book to the library manually (without API lookup).
    
    Args:
        book_request: Request containing book information
        
    Returns:
        The added book information
        
    Raises:
        HTTPException: If book already exists or validation fails
    """
    if not all([book_request.title.strip(), book_request.author.strip(), book_request.isbn.strip()]):
        raise HTTPException(status_code=400, detail="Title, author, and ISBN are all required")
    
    # Check if book already exists
    if library.find_book(book_request.isbn):
        raise HTTPException(status_code=409, detail=f"Book with ISBN {book_request.isbn} already exists")
    
    # Create and add book
    book = Book(book_request.title, book_request.author, book_request.isbn)
    library.books.append(book)
    library.save_books()
    
    return BookResponse(
        title=book.title,
        author=book.author,
        isbn=book.isbn
    )

@app.get("/books/{isbn}", response_model=BookResponse)
async def get_book_by_isbn(isbn: str):
    """
    Get a specific book by ISBN.
    
    Args:
        isbn: The ISBN of the book to retrieve
        
    Returns:
        The book information
        
    Raises:
        HTTPException: If book is not found
    """
    book = library.find_book(isbn)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with ISBN {isbn} not found")
    
    return BookResponse(
        title=book.title,
        author=book.author,
        isbn=book.isbn
    )

@app.delete("/books/{isbn}", response_model=MessageResponse)
async def remove_book(isbn: str):
    """
    Remove a book from the library by ISBN.
    
    Args:
        isbn: The ISBN of the book to remove
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If book is not found
    """
    book = library.find_book(isbn)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with ISBN {isbn} not found")
    
    library.books.remove(book)
    library.save_books()
    
    return MessageResponse(message=f"Book '{book.title}' by {book.author} (ISBN: {isbn}) has been removed")

@app.get("/health", response_model=MessageResponse)
async def health_check():
    """Health check endpoint."""
    return MessageResponse(message="API is healthy")

@app.get("/stats")
async def get_library_stats():
    """
    Get library statistics.
    
    Returns:
        Dictionary with library statistics
    """
    return {
        "total_books": len(library.books),
        "library_file": library.filename,
        "api_version": "1.0.0"
    }

# Add CORS middleware if needed (for frontend integration)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)