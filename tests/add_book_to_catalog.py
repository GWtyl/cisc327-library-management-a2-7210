import pytest
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import services.library_service as ls
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
    
def test_borrow_book_success(monkeypatch):
    """Test successful book borrowing with valid inputs"""
    # Setup mocks
    mock_get_book = MagicMock(return_value={
        'id': 1,
        'title': 'Python Programming',
        'author': 'John Doe',
        'isbn': '9780123456789',
        'available_copies': 3
    })
    mock_get_count = MagicMock(return_value=2)
    mock_insert_borrow = MagicMock(return_value=True)
    mock_update_avail = MagicMock(return_value=True)
    
    monkeypatch.setattr('library_service.get_book_by_id', mock_get_book)
    monkeypatch.setattr('library_service.get_patron_borrow_count', mock_get_count)
    monkeypatch.setattr('library_service.insert_borrow_record', mock_insert_borrow)
    monkeypatch.setattr('library_service.update_book_availability', mock_update_avail)
    
    # Execute
    success, message = ls.borrow_book_by_patron('123456', 1)
    
    # Assert
    assert success is True
    assert 'Successfully borrowed' in message
    mock_update_avail.assert_called_once_with(1, -1)


def test_borrow_book_invalid_patron_id(monkeypatch):
    """Test borrowing with invalid patron ID format"""
    # Test empty patron ID
    success, message = ls.borrow_book_by_patron('', 1)
    assert success is False
    assert 'Invalid patron ID' in message
    
    # Test too short patron ID
    success, message = ls.borrow_book_by_patron('12345', 1)
    assert success is False
    assert 'exactly 6 digits' in message
    
    # Test too long patron ID
    success, message = ls.borrow_book_by_patron('1234567', 1)
    assert success is False
    assert 'exactly 6 digits' in message
    
    # Test non-numeric patron ID
    success, message = ls.borrow_book_by_patron('ABC123', 1)
    assert success is False
    assert 'Invalid patron ID' in message


def test_borrow_book_not_found(monkeypatch):
    """Test borrowing when book doesn't exist"""
    mock_get_book = MagicMock(return_value=None)
    monkeypatch.setattr('library_service.get_book_by_id', mock_get_book)
    
    success, message = ls.borrow_book_by_patron('123456', 999)
    
    assert success is False
    assert 'Book not found' in message


def test_borrow_book_not_available(monkeypatch):
    """Test borrowing when book has no available copies"""
    mock_get_book = MagicMock(return_value={
        'id': 1,
        'title': 'Python Programming',
        'available_copies': 0
    })
    monkeypatch.setattr('library_service.get_book_by_id', mock_get_book)
    
    success, message = ls.borrow_book_by_patron('123456', 1)
    
    assert success is False
    assert 'not available' in message


def test_borrow_book_borrowing_limit_reached(monkeypatch):
    """Test borrowing when patron has reached maximum borrowing limit"""
    mock_get_book = MagicMock(return_value={
        'id': 6,
        'available_copies': 2
    })
    mock_get_count = MagicMock(return_value=5)
    
    monkeypatch.setattr('library_service.get_book_by_id', mock_get_book)
    monkeypatch.setattr('library_service.get_patron_borrow_count', mock_get_count)
    
    success, message = ls.borrow_book_by_patron('123456', 6)
    
    assert success is False
    assert 'maximum borrowing limit' in message