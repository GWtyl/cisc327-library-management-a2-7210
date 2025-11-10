import pytest
from services.library_service import (
    add_book_to_catalog
)

def test_add_book_valid_input(monkeypatch):
    """Test adding a book with valid input."""
    monkeypatch.setattr("library_service.get_book_by_isbn", lambda isbn: None)
    monkeypatch.setattr("library_service.insert_book", lambda *args, **kwargs: True)
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    assert success is True
    assert "successfully added" in message.lower()


def test_add_book_invalid_isbn(monkeypatch):
    """Test adding a book with an invalid ISBN length."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123", 5)
    assert success is False
    assert "13 digits" in message


def test_add_book_duplicate_isbn(monkeypatch):
    """Test adding a book with an ISBN that already exists."""
    monkeypatch.setattr("library_service.get_book_by_isbn", lambda isbn: {"title": "Existing"})
    success, message = add_book_to_catalog("Another Book", "Another Author", "1234567890123", 3)
    assert success is False
    assert "already exists" in message.lower()


def test_add_book_invalid_copies(monkeypatch):
    """Test adding a book with invalid copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    assert success is False
    assert "positive integer" in message.lower()