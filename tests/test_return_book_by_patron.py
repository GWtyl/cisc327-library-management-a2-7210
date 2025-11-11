import pytest
from services.library_service import (
    return_book_by_patron
)

def test_return_book_invalid_patron_id():
    """Invalid patron ID (non-digit or wrong length) should fail."""
    success, message = return_book_by_patron("abc", 99)
    assert success is False
    assert message == "Invalid patron ID. Must be exactly 6 digits."


def test_return_book_edge_case_empty_patron():
    """Empty patron ID should fail validation."""
    success, message = return_book_by_patron("", 10)
    assert success is False
    assert message == "Invalid patron ID. Must be exactly 6 digits."


def test_return_book_nonexistent_book(monkeypatch):
    """If the book ID does not exist, function should return appropriate error."""
    # Mock get_book_by_id to return None (book not found)
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda book_id: None)

    success, message = return_book_by_patron("123456", 999)
    assert success is False
    assert message == "Book not found."


def test_return_book_no_active_record(monkeypatch):
    """If patron never borrowed this book, should return error."""
    mock_get_book = lambda book_id: {"id": 1, "title": "Test Book"}
    mock_get_record = lambda patron_id, book_id: None

    monkeypatch.setattr("services.library_service.get_book_by_id", mock_get_book)
    monkeypatch.setattr("services.library_service.get_borrow_record_by_patron_and_book", mock_get_record)

    success, message = return_book_by_patron("123456", 1)
    assert success is False
    assert message == "No active borrow record found for this book and patron."
