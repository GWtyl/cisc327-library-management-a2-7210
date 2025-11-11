import pytest
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from services import library_service as ls
# from services.library_service import (
#     get_patron_status_report
# )

def test_get_patron_status_returns_dict():
    """Ensure get_patron_status_report returns a dict."""
    result = ls.get_patron_status_report("123456")
    assert isinstance(result, dict)

def test_get_patron_status_empty_by_default():
    """Ensure default returned dict is empty."""
    result = ls.get_patron_status_report("123456")
    assert result == {}

def test_get_patron_status_invalid_id():
    """Even invalid patron IDs return empty dict."""
    result = ls.get_patron_status_report("badid")
    assert result == {}

def test_get_patron_status_edge_case_empty_id():
    """Edge case: empty patron ID returns empty dict."""
    result = ls.get_patron_status_report("")
    assert result == {}

def test_get_patron_status_with_active_borrows(monkeypatch):
    """Test patron status with active borrowed books"""
    mock_get_all_records = MagicMock(return_value=[
        {
            'id': 1,
            'book_id': 1,
            'borrow_date': '2025-10-01',
            'due_date': (datetime.now() + timedelta(days=5)).isoformat(),
            'return_date': None
        },
        {
            'id': 2,
            'book_id': 2,
            'borrow_date': '2025-10-05',
            'due_date': (datetime.now() + timedelta(days=9)).isoformat(),
            'return_date': None
        }
    ])
    
    mock_get_book = MagicMock(side_effect=[
        {'id': 1, 'title': 'Book 1', 'author': 'Author 1'},
        {'id': 2, 'title': 'Book 2', 'author': 'Author 2'}
    ])
    
    monkeypatch.setattr('library_service.get_all_patron_borrow_records', mock_get_all_records)
    monkeypatch.setattr('library_service.get_book_by_id', mock_get_book)
    
    result = ls.get_patron_status_report('123456')
    
    assert result['patron_id'] == '123456'
    assert result['num_books_borrowed'] == 2
    assert result['total_late_fees'] == 0.0
    assert len(result['currently_borrowed']) == 2


def test_get_patron_status_no_active_borrows(monkeypatch):
    """Test patron status with no currently borrowed books"""
    mock_get_all_records = MagicMock(return_value=[])
    
    monkeypatch.setattr('library_service.get_all_patron_borrow_records', mock_get_all_records)
    
    result = ls.get_patron_status_report('123456')
    
    assert result['num_books_borrowed'] == 0
    assert result['total_late_fees'] == 0.0
    assert len(result['currently_borrowed']) == 0


def test_get_patron_status_invalid_patron_id(monkeypatch):
    """Test patron status with invalid patron ID"""
    result = ls.get_patron_status_report('')
    
    assert 'error' in result
    assert result['error'] == 'Invalid patron ID'


def test_get_patron_status_with_overdue_books(monkeypatch):
    """Test patron status with overdue books"""
    past_due_date = (datetime.now() - timedelta(days=5)).isoformat()
    
    mock_get_all_records = MagicMock(return_value=[
        {
            'id': 1,
            'book_id': 1,
            'borrow_date': '2025-10-01',
            'due_date': past_due_date,
            'return_date': None
        }
    ])
    
    mock_get_book = MagicMock(return_value={
        'id': 1,
        'title': 'Overdue Book',
        'author': 'Some Author'
    })
    
    monkeypatch.setattr('library_service.get_all_patron_borrow_records', mock_get_all_records)
    monkeypatch.setattr('library_service.get_book_by_id', mock_get_book)
    
    result = ls.get_patron_status_report('123456')
    
    assert result['total_late_fees'] == 2.50  # 5 days * $0.50
    assert result['num_books_borrowed'] == 1
    assert result['currently_borrowed'][0]['late_fee'] == 2.50


def test_get_patron_status_with_history(monkeypatch):
    """Test patron status includes borrowing history"""
    mock_get_all_records = MagicMock(return_value=[
        {
            'id': 1,
            'book_id': 1,
            'borrow_date': '2025-09-01',
            'due_date': '2025-09-15',
            'return_date': '2025-09-14'
        },
        {
            'id': 2,
            'book_id': 2,
            'borrow_date': '2025-10-01',
            'due_date': (datetime.now() + timedelta(days=5)).isoformat(),
            'return_date': None
        }
    ])
    
    mock_get_book = MagicMock(side_effect=[
        {'id': 1, 'title': 'Book 1', 'author': 'Author 1'},
        {'id': 2, 'title': 'Book 2', 'author': 'Author 2'}
    ])
    
    monkeypatch.setattr('library_service.get_all_patron_borrow_records', mock_get_all_records)
    monkeypatch.setattr('library_service.get_book_by_id', mock_get_book)
    
    result = ls.get_patron_status_report('123456')
    
    assert len(result['borrowing_history']) == 2
    assert result['borrowing_history'][0]['return_date'] == '2025-09-14'
    assert 'return_date' not in result['borrowing_history'][1]
