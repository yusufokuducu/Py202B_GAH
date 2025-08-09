import json

class book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn

    def __str__(self):
        return f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}"
    
    def to_dict(self):
        return {"title": self.title, "author": self.author, "isbn": self.isbn}
    
class library:
    def __init__(self, filename="Library.json"):
        self.filename = filename
        self.books = self.load_books()

    def load_books(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                return [book(b['title'], b['author'], b['isbn']) for b in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_books(self):
        with open(self.filename, "w") as f:
            json.dump([b.to_dict() for b in self.books], f, indent=4)
    
    def add_book(self, book):
        self.books.append(book)
        self.save_books()
        print(f"Added: {book}")
    
    def remove_book(self, isbn):
        book_to_remove = self.find_book(isbn)
        if book_to_remove:
            self.books.remove(book_to_remove)
            self.save_books()
            print(f"Removed book with ISBN: {isbn}")
        else:
            print(f"Book with ISBN {isbn} not found.")
    
    def find_book(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None
    
    def list_books(self):
        if not self.books:
            print("The library is empty.")
            return
        
        print("--- Library Books ---")
        for book in self.books:
            print(book)
        print("---------")