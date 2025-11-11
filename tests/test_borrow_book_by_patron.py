import pytest
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import services.library_service as ls
from datetime import datetime, timedelta

def test_borrow_book_valid(monkeypatch):
    """Test successful borrowing of a book."""
    mock_book = {"id": 1, "title": "Sample", "available_copies": 2}
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda book_id: mock_book)
    monkeypatch.setattr("services.library_service.get_patron_borrow_count", lambda pid: 2)
    monkeypatch.setattr("services.library_service.insert_borrow_record", lambda *args: True)
    monkeypatch.setattr("services.library_service.update_book_availability", lambda *args: True)

    success, message = ls.borrow_book_by_patron("123456", 1)
    assert success is True
    assert "successfully borrowed" in message.lower()


def test_borrow_book_invalid_patron_id():
    """Test borrow with invalid patron ID."""
    success, message = ls.borrow_book_by_patron("12A45", 1)
    assert success is False
    assert "invalid patron id" in message.lower()


def test_borrow_book_not_found(monkeypatch):
    """Test borrow with nonexistent book ID."""
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda book_id: None)
    success, message = ls.borrow_book_by_patron("123456", 1)
    assert success is False
    assert "not found" in message.lower()


def test_borrow_book_unavailable(monkeypatch):
    """Test borrowing a book with 0 available copies."""
    mock_book = {"id": 1, "title": "Unavailable", "available_copies": 0}
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda book_id: mock_book)

    success, message = ls.borrow_book_by_patron("123456", 1)
    assert success is False
    assert "not available" in message.lower()


def test_borrow_book_limit_reached(monkeypatch):
    """Test borrowing when patron has max limit of 5 books."""
    mock_book = {"id": 1, "title": "Limit Book", "available_copies": 1}
    monkeypatch.setattr("services.library_service.get_book_by_id", lambda book_id: mock_book)
    monkeypatch.setattr("services.library_service.get_patron_borrow_count", lambda pid: 6)

    success, message = ls.borrow_book_by_patron("123456", 1)
    assert success is False
    assert "maximum borrowing limit" in message.lower()

def test_return_book_on_time(monkeypatch):
    """Test returning a book before due date (no late fee)"""
    # Setup
    future_due_date = (datetime.now() + timedelta(days=5)).isoformat()
    
    mock_get_book = MagicMock(return_value={
        'id': 1,
        'title': 'Python Programming',
        'available_copies': 2
    })
    mock_get_borrow = MagicMock(return_value={
        'id': 1,
        'patron_id': '123456',
        'book_id': 1,
        'due_date': future_due_date
    })
    mock_update_return = MagicMock(return_value=True)
    mock_update_avail = MagicMock(return_value=True)
    
    monkeypatch.setattr('services.library_service.get_book_by_id', mock_get_book)
    monkeypatch.setattr('services.library_service.get_borrow_record_by_patron_and_book', mock_get_borrow)
    monkeypatch.setattr('services.library_service.update_borrow_record_return_date', mock_update_return)
    monkeypatch.setattr('services.library_service.update_book_availability', mock_update_avail)
    
    # Execute
    success, message = ls.return_book_by_patron('123456', 1)
    
    # Assert
    assert success is True
    assert 'No late fees' in message
    mock_update_avail.assert_called_once_with(1, 1)


def test_return_book_late(monkeypatch):
    """Test returning a book after due date (with late fee)"""
    # Setup - 5 days late
    past_due_date = (datetime.now() - timedelta(days=5)).isoformat()
    
    mock_get_book = MagicMock(return_value={
        'id': 1,
        'title': 'Python Programming',
        'available_copies': 2
    })
    mock_get_borrow = MagicMock(return_value={
        'id': 1,
        'patron_id': '123456',
        'book_id': 1,
        'due_date': past_due_date
    })
    mock_update_return = MagicMock(return_value=True)
    mock_update_avail = MagicMock(return_value=True)
    
    monkeypatch.setattr('services.library_service.get_book_by_id', mock_get_book)
    monkeypatch.setattr('services.library_service.get_borrow_record_by_patron_and_book', mock_get_borrow)
    monkeypatch.setattr('services.library_service.update_borrow_record_return_date', mock_update_return)
    monkeypatch.setattr('services.library_service.update_book_availability', mock_update_avail)
    
    # Execute
    success, message = ls.return_book_by_patron('123456', 1)
    
    # Assert
    assert success is True
    assert 'Late fee: $2.50' in message  # 5 days * $0.50
    assert '5 days overdue' in message


def test_return_book_no_active_borrow(monkeypatch):
    """Test returning a book with no active borrow record"""
    mock_get_book = MagicMock(return_value={
        'id': 1,
        'title': 'Python Programming'
    })
    mock_get_borrow = MagicMock(return_value=None)
    
    monkeypatch.setattr('services.library_service.get_book_by_id', mock_get_book)
    monkeypatch.setattr('services.library_service.get_borrow_record_by_patron_and_book', mock_get_borrow)
    
    success, message = ls.return_book_by_patron('123456', 1)
    
    assert success is False
    assert 'No active borrow record found' in message


def test_return_book_invalid_patron_id(monkeypatch):
    """Test return with invalid patron ID"""
    success, message = ls.return_book_by_patron('', 1)
    
    assert success is False
    assert 'Invalid patron ID' in message