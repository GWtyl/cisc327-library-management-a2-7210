import pytest
from library_service import (
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