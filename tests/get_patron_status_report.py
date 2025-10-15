import pytest
from library_service import (
    get_patron_status_report
)

def test_get_patron_status_returns_dict():
    """Ensure get_patron_status_report returns a dict."""
    result = get_patron_status_report("123456")
    assert isinstance(result, dict)

def test_get_patron_status_empty_by_default():
    """Ensure default returned dict is empty."""
    result = get_patron_status_report("123456")
    assert result == {}

def test_get_patron_status_invalid_id():
    """Even invalid patron IDs return empty dict."""
    result = get_patron_status_report("badid")
    assert result == {}

def test_get_patron_status_edge_case_empty_id():
    """Edge case: empty patron ID returns empty dict."""
    result = get_patron_status_report("")
    assert result == {}