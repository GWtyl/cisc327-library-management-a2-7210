import pytest
from datetime import datetime, timedelta
from library_service import (
    borrow_book_by_patron
)

def test_borrow_book_valid(monkeypatch):
    """Test successful borrowing of a book."""
    mock_book = {"id": 1, "title": "Sample", "available_copies": 2}
    monkeypatch.setattr("library_service.get_book_by_id", lambda book_id: mock_book)
    monkeypatch.setattr("library_service.get_patron_borrow_count", lambda pid: 2)
    monkeypatch.setattr("library_service.insert_borrow_record", lambda *args: True)
    monkeypatch.setattr("library_service.update_book_availability", lambda *args: True)

    success, message = borrow_book_by_patron("123456", 1)
    assert success is True
    assert "successfully borrowed" in message.lower()


def test_borrow_book_invalid_patron_id():
    """Test borrow with invalid patron ID."""
    success, message = borrow_book_by_patron("12A45", 1)
    assert success is False
    assert "invalid patron id" in message.lower()


def test_borrow_book_not_found(monkeypatch):
    """Test borrow with nonexistent book ID."""
    monkeypatch.setattr("library_service.get_book_by_id", lambda book_id: None)
    success, message = borrow_book_by_patron("123456", 1)
    assert success is False
    assert "not found" in message.lower()


def test_borrow_book_unavailable(monkeypatch):
    """Test borrowing a book with 0 available copies."""
    mock_book = {"id": 1, "title": "Unavailable", "available_copies": 0}
    monkeypatch.setattr("library_service.get_book_by_id", lambda book_id: mock_book)

    success, message = borrow_book_by_patron("123456", 1)
    assert success is False
    assert "not available" in message.lower()


def test_borrow_book_limit_reached(monkeypatch):
    """Test borrowing when patron has max limit of 5 books."""
    mock_book = {"id": 1, "title": "Limit Book", "available_copies": 1}
    monkeypatch.setattr("library_service.get_book_by_id", lambda book_id: mock_book)
    monkeypatch.setattr("library_service.get_patron_borrow_count", lambda pid: 6)

    success, message = borrow_book_by_patron("123456", 1)
    assert success is False
    assert "maximum borrowing limit" in message.lower()
