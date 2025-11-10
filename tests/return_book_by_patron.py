import pytest
from services.library_service import (
    return_book_by_patron
)

def test_return_book_placeholder_message():
    """Ensure return_book_by_patron returns placeholder message."""
    success, message = return_book_by_patron("123456", 1)
    assert success is False
    assert "not yet implemented" in message.lower()

def test_return_book_invalid_patron_id():
    """Even invalid patron IDs should still return not implemented."""
    success, message = return_book_by_patron("abc", 99)
    assert success is False
    assert "not yet implemented" in message.lower()

def test_return_book_invalid_book_id():
    """Even invalid book IDs should return not implemented."""
    success, message = return_book_by_patron("123456", -1)
    assert success is False
    assert "not yet implemented" in message.lower()

def test_return_book_edge_case_empty_patron():
    """Edge case: empty patron ID still not implemented."""
    success, message = return_book_by_patron("", 10)
    assert success is False
    assert "not yet implemented" in message.lower()
