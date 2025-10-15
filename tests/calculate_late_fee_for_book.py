import pytest
from library_service import (
    calculate_late_fee_for_book
)

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