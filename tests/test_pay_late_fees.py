import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway 

#stubbing test
def test_pay_late_fees_successful_payment(mocker):
    """Test successful payment with stubs for DB functions and mock for gateway."""
    # Stub database functions
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 5.00})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "Python Basics"})

    # Mock payment gateway
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")

    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    # Assertions
    assert success is True
    assert "Payment successful" in msg
    assert txn_id == "txn_123"

    # Verify mock interactions
    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=5.00,
        description="Late fees for 'Python Basics'"
    )


def test_pay_late_fees_payment_declined(mocker):
    """Test when payment gateway declines the payment."""
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 5.00})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "Python Basics"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, None, "Card declined")

    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "Card declined" in msg
    assert txn_id is None

    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fees_invalid_patron_id(mocker):
    """Invalid patron ID should short-circuit before calling the payment gateway."""
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn_id = pay_late_fees("abc", 1, mock_gateway)

    assert success is False
    assert "Invalid patron ID" in msg
    assert txn_id is None

    # Verify gateway not used
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_fee(mocker):
    """No late fees -> gateway should not be called."""
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0})
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "No late fees" in msg
    assert txn_id is None
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_network_error(mocker):
    """Handle exceptions from payment gateway gracefully."""
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 5.00})
    mocker.patch("services.library_service.get_book_by_id",
                 return_value={"id": 1, "title": "Python Basics"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network down")

    success, msg, txn_id = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "Network down" in msg
    assert txn_id is None

    mock_gateway.process_payment.assert_called_once()