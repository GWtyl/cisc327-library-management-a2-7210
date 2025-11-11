import pytest
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import services.library_service as ls
from services.library_service import (
    calculate_late_fee_for_book
)
''' old test
def test_calculate_late_fee_returns_dict():
    """Ensure calculate_late_fee returns a dict."""
    result = calculate_late_fee_for_book("123456", 1)
    assert isinstance(result, dict)

def test_calculate_late_fee_contains_status():
    """Ensure returned dict contains status key."""
    result = calculate_late_fee_for_book("123456", 1)
    assert "status" in result
    assert "not implemented" in result["status"].lower()

def test_calculate_late_fee_has_default_fee():
    """Ensure default fee is 0.00."""
    result = calculate_late_fee_for_book("123456", 1)
    assert result.get("fee_amount", None) == 0.00

def test_calculate_late_fee_has_default_days():
    """Ensure default overdue days is 0."""
    result = calculate_late_fee_for_book("123456", 1)
    assert result.get("days_overdue", None) == 0
'''    
def test_calculate_late_fee_with_overdue_book(monkeypatch):
    """Test late fee calculation with overdue book"""
    # Setup - 5 days overdue
    past_due_date = (datetime.now() - timedelta(days=5)).isoformat()
    
    mock_get_borrow = MagicMock(return_value={
        'id': 1,
        'patron_id': '123456',
        'book_id': 1,
        'due_date': past_due_date,
        'return_date': None
    })
    
    monkeypatch.setattr('library_service.get_borrow_record_by_patron_and_book', mock_get_borrow)
    
    # Execute
    result = ls.calculate_late_fee_for_book('123456', 1)
    
    # Assert
    assert result['fee_amount'] == 2.50  # 5 days * $0.50
    assert result['days_overdue'] == 5
    assert result['status'] == 'Overdue'

def test_calculate_late_fee_not_overdue(monkeypatch):
    """Test late fee calculation with book not yet overdue"""
    # Setup - due in 5 days
    future_due_date = (datetime.now() + timedelta(days=5)).isoformat()
    
    mock_get_borrow = MagicMock(return_value={
        'id': 1,
        'patron_id': '123456',
        'book_id': 1,
        'due_date': future_due_date,
        'return_date': None
    })
    
    monkeypatch.setattr('library_service.get_borrow_record_by_patron_and_book', mock_get_borrow)
    
    # Execute
    result = ls.calculate_late_fee_for_book('123456', 1)
    
    # Assert
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert result['status'] == 'Not overdue'


def test_calculate_late_fee_no_borrow_record(monkeypatch):
    """Test late fee calculation with no active borrow record"""
    mock_get_borrow = MagicMock(return_value=None)
    monkeypatch.setattr('library_service.get_borrow_record_by_patron_and_book', mock_get_borrow)
    
    result = ls.calculate_late_fee_for_book('123456', 1)
    
    assert result['fee_amount'] == 0.00
    assert result['status'] == 'No active borrow record found'


def test_calculate_late_fee_already_returned(monkeypatch):
    """Test late fee calculation for already returned book"""
    mock_get_borrow = MagicMock(return_value={
        'id': 1,
        'patron_id': '123456',
        'book_id': 1,
        'due_date': '2025-10-01',
        'return_date': '2025-10-05'
    })
    
    monkeypatch.setattr('library_service.get_borrow_record_by_patron_and_book', mock_get_borrow)
    
    result = ls.calculate_late_fee_for_book('123456', 1)
    
    assert result['fee_amount'] == 0.00
    assert result['status'] == 'Book already returned'


def test_calculate_late_fee_maximum_cap(monkeypatch):
    """Test late fee calculation with maximum cap of $15.00"""
    # Setup - 30 days overdue (would be $17.50 without cap)
    past_due_date = (datetime.now() - timedelta(days=30)).isoformat()
    
    mock_get_borrow = MagicMock(return_value={
        'id': 1,
        'patron_id': '123456',
        'book_id': 1,
        'due_date': past_due_date,
        'return_date': None
    })
    
    monkeypatch.setattr('library_service.get_borrow_record_by_patron_and_book', mock_get_borrow)
    
    result = ls.calculate_late_fee_for_book('123456', 1)
    
    assert result['fee_amount'] == 15.00  # Capped at $15.00
    assert result['days_overdue'] == 30
