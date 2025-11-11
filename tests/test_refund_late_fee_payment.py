import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

def test_refund_late_fee_successful(mocker):
    """Test successful refund with mock verification."""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund processed")

    success, msg = refund_late_fee_payment("txn_123", 5.00, mock_gateway)

    assert success is True
    assert msg == "Refund processed"

    mock_gateway.refund_payment.assert_called_once_with("txn_123", 5.00)


def test_refund_late_fee_invalid_transaction():
    """Invalid transaction ID should fail immediately."""
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg = refund_late_fee_payment("bad_txn", 5.00, mock_gateway)

    assert success is False
    assert "Invalid transaction ID" in msg
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_invalid_amounts(mock_gateway=Mock(spec=PaymentGateway)):
    """Reject invalid refund amounts: negative, zero, or over $15."""
    # Negative amount
    success, msg = refund_late_fee_payment("txn_123", -5, mock_gateway)
    assert success is False
    assert "greater than 0" in msg

    # Zero amount
    success, msg = refund_late_fee_payment("txn_123", 0, mock_gateway)
    assert success is False
    assert "greater than 0" in msg

    # Exceeds maximum
    success, msg = refund_late_fee_payment("txn_123", 20.0, mock_gateway)
    assert success is False
    assert "exceeds maximum" in msg

    # Gateway should never be called
    mock_gateway.refund_payment.assert_not_called()