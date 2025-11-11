import pytest
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import services.library_service as ls
from services.library_service import (
    search_books_in_catalog
)

def test_search_books_returns_list():
    """Ensure search_books_in_catalog returns a list."""
    result = search_books_in_catalog("anything", "title")
    assert isinstance(result, list)

def test_search_books_empty_result_default():
    """Ensure default return is an empty list."""
    result = search_books_in_catalog("Harry", "title")
    assert result == []

def test_search_books_case_insensitivity_placeholder():
    """Even with different case, placeholder still returns empty."""
    result = search_books_in_catalog("harry", "author")
    assert result == []

def test_search_books_invalid_type_placeholder():
    """Invalid search type still returns empty list."""
    result = search_books_in_catalog("12345", "nonsense")
    assert result == []
    
def test_search_books_by_title(monkeypatch):
    """Test searching books by title"""
    mock_get_all_books = MagicMock(return_value=[
        {'id': 1, 'title': 'Python Programming', 'author': 'John Doe', 'isbn': '1111111111111'},
        {'id': 2, 'title': 'Java Basics', 'author': 'Jane Smith', 'isbn': '2222222222222'},
        {'id': 3, 'title': 'Advanced Python', 'author': 'Bob Wilson', 'isbn': '3333333333333'}
    ])
    
    monkeypatch.setattr('library_service.get_all_books', mock_get_all_books)
    
    result = ls.search_books_in_catalog('python', 'title')
    
    assert len(result) == 2
    assert all('python' in book['title'].lower() for book in result)


def test_search_books_by_author(monkeypatch):
    """Test searching books by author name"""
    mock_get_all_books = MagicMock(return_value=[
        {'id': 1, 'title': 'Python Programming', 'author': 'John Doe', 'isbn': '1111111111111'},
        {'id': 2, 'title': 'Java Basics', 'author': 'John Smith', 'isbn': '2222222222222'}
    ])
    
    monkeypatch.setattr('library_service.get_all_books', mock_get_all_books)
    
    result = ls.search_books_in_catalog('john', 'author')
    
    assert len(result) == 2


def test_search_books_by_isbn(monkeypatch):
    """Test searching books by ISBN (exact match)"""
    mock_get_all_books = MagicMock(return_value=[
        {'id': 1, 'title': 'Database Systems', 'author': 'Alice Johnson', 'isbn': '9781234567890'},
        {'id': 2, 'title': 'Web Development', 'author': 'Bob Smith', 'isbn': '9785678901234'}
    ])
    
    monkeypatch.setattr('library_service.get_all_books', mock_get_all_books)
    
    result = ls.search_books_in_catalog('9781234567890', 'isbn')
    
    assert len(result) == 1
    assert result[0]['isbn'] == '9781234567890'


def test_search_books_empty_query(monkeypatch):
    """Test search with empty query string"""
    result = ls.search_books_in_catalog('', 'title')
    
    assert len(result) == 0


def test_search_books_invalid_type(monkeypatch):
    """Test search with invalid search type"""
    result = ls.search_books_in_catalog('python', 'invalid_type')
    
    assert len(result) == 0


def test_search_books_no_results(monkeypatch):
    """Test search with no matching results"""
    mock_get_all_books = MagicMock(return_value=[
        {'id': 1, 'title': 'Python Programming', 'author': 'John Doe', 'isbn': '1111111111111'}
    ])
    
    monkeypatch.setattr('library_service.get_all_books', mock_get_all_books)
    
    result = ls.search_books_in_catalog('nonexistent', 'title')
    
    assert len(result) == 0