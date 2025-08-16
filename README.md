# Library Management System

A comprehensive library management system built with Python, featuring a console application, API integration, and web service. This project demonstrates Object-Oriented Programming (OOP), external API usage, and FastAPI web service development.

## Features

### Phase 1: Console Application (OOP)
-  **Book Management**: Add, remove, find, and list books
-  **Data Persistence**: JSON file storage (`library.json`)
-  **Object-Oriented Design**: Clean `Book` and `Library` classes
-  **Interactive Menu**: User-friendly command-line interface

### Phase 2: API Integration
-  **Open Library Integration**: Fetch book data using ISBN
-  **Smart Book Addition**: Add books with just ISBN (auto-fetch title/author)
-  **Error Handling**: Robust handling of network errors and invalid ISBNs
-  **Dual Input Methods**: Both API-based and manual book entry

### Phase 3: Web Service (FastAPI)
-  **RESTful API**: Complete CRUD operations via HTTP endpoints
-  **Interactive Documentation**: Auto-generated Swagger UI at `/docs`
-  **Data Validation**: Pydantic models for request/response validation
-  **CORS Support**: Ready for frontend integration

## Project Structure

```
Py202B_GAH/
├── main.py                 # Core library classes and console app
├── api.py                  # FastAPI web service
├── test_library.py         # Tests for core functionality
├── test_api_integration.py # Tests for API integration
├── test_fastapi.py         # Tests for FastAPI endpoints
├── requirements.txt        # Project dependencies
├── library.json           # Data storage (auto-created)
├── README.md              # This file
└── project-rules-and-guide.md # Project requirements
```

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yusufokuducu/Py202B_GAH
cd Py202B_GAH
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
python -m pytest -v
```

## Usage

### Console Application (Phases 1 & 2)

Start the interactive console application:

```bash
python main.py
```

**Menu Options:**
1. **Add book by ISBN** - Fetches book data from Open Library API
2. **Add book manually** - Enter title, author, and ISBN manually  
3. **Remove a book** - Delete by ISBN
4. **List all books** - Display all books in library
5. **Find a book** - Search by ISBN
6. **Exit** - Close application

**Example Usage:**
```
=== Library Management System ===
1. Add book by ISBN (from Open Library API)
2. Add book manually
3. Remove a book
4. List all books
5. Find a book
6. Exit
==========================================
Enter your choice (1-6): 1

--- Add Book by ISBN ---
Enter the ISBN: 9780451524935
Fetching book information for ISBN 9780451524935...
Successfully added: Nineteen Eighty-Four by George Orwell (ISBN: 9780451524935)
```

### Web Service (Phase 3)

#### Start the API Server
```bash
uvicorn api:app --reload
```

The server will start at `http://localhost:8000`

#### Interactive Documentation
Visit `http://localhost:8000/docs` for the interactive Swagger UI documentation.

#### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message |
| `GET` | `/books` | Get all books |
| `POST` | `/books` | Add book by ISBN (API lookup) |
| `POST` | `/books/manual` | Add book manually |
| `GET` | `/books/{isbn}` | Get specific book by ISBN |
| `DELETE` | `/books/{isbn}` | Remove book by ISBN |
| `GET` | `/health` | Health check |
| `GET` | `/stats` | Library statistics |

#### Example API Calls

**Get all books:**
```bash
curl -X GET "http://localhost:8000/books"
```

**Add book by ISBN:**
```bash
curl -X POST "http://localhost:8000/books" \
     -H "Content-Type: application/json" \
     -d '{"isbn": "9780451524935"}'
```

**Add book manually:**
```bash
curl -X POST "http://localhost:8000/books/manual" \
     -H "Content-Type: application/json" \
     -d '{"title": "1984", "author": "George Orwell", "isbn": "9780451524935"}'
```

**Remove book:**
```bash
curl -X DELETE "http://localhost:8000/books/9780451524935"
```

## Testing

The project includes comprehensive test suites for all components:

### Run All Tests
```bash
python -m pytest -v
```

### Run Specific Test Suites
```bash
# Core library tests
python -m pytest test_library.py -v

# API integration tests  
python -m pytest test_api_integration.py -v

# FastAPI tests
python -m pytest test_fastapi.py -v
```

### Test Coverage
- **25 total tests** covering all functionality
- **Unit tests** for Book and Library classes
- **Integration tests** for Open Library API
- **API endpoint tests** for FastAPI service
- **Error handling** and edge case coverage

## Dependencies

- **httpx**: HTTP client for API calls
- **fastapi**: Modern web framework for APIs
- **uvicorn**: ASGI server for FastAPI
- **pydantic**: Data validation and serialization
- **pytest**: Testing framework

## Data Storage

- **Format**: JSON
- **File**: `library.json` (auto-created)
- **Structure**: Array of book objects with title, author, and ISBN
- **Persistence**: Automatic save on every modification

## API Integration

### Open Library API
- **Base URL**: `https://openlibrary.org/`
- **Endpoint**: `/isbn/{isbn}.json`
- **Features**: Automatic book data fetching
- **Error Handling**: Graceful handling of API failures

## Development Features

- **Type Hints**: Full typing support for better IDE integration
- **Error Handling**: Comprehensive exception handling
- **Documentation**: Docstrings for all classes and methods
- **CORS**: Cross-origin resource sharing enabled
- **Validation**: Pydantic models for data validation
- **Logging**: Basic logging for debugging

## Example Data Flow

1. **User enters ISBN** → 
2. **System calls Open Library API** → 
3. **API returns book data** → 
4. **System creates Book object** → 
5. **Book saved to library.json** → 
6. **Success confirmation to user**

## Future Enhancements

- **Database Integration**: SQLite or PostgreSQL
- **User Authentication**: JWT-based auth system
- **Frontend Interface**: React/Vue.js web interface
- **Book Ratings**: User rating and review system
- **Search Enhancement**: Full-text search capabilities
- **Docker Support**: Containerization
- **Caching**: Redis for API response caching


---

**Project Status**: ✅ **All Three Phases Completed Successfully**

- ✅ Phase 1: OOP Console Application
- ✅ Phase 2: API Integration 
- ✅ Phase 3: FastAPI Web Service