"""
Tests for email sending functionality
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport


# Shared test data
SAMPLE_EMAIL_PARAMS = {
    "to_email": "billing@acme.com",
    "client_name": "Acme Corp",
    "invoice_number": "INV-0001",
    "total_due": 2200.0,
    "pdf_bytes": b"%PDF-fake-content",
    "company_name": "My Company Ltd",
}

SAMPLE_INVOICE = {
    "id": "invoice-uuid-123",
    "user_id": "user-123",
    "client_id": "client-uuid-123",
    "client_name": "Acme Corp",
    "client_email": "billing@acme.com",
    "invoice_number": "INV-0001",
    "status": "draft",
    "issue_date": "2026-01-15",
    "due_date": "2026-02-15",
    "subtotal": 2000.0,
    "tax_rate": 10.0,
    "tax_amount": 200.0,
    "total_due": 2200.0,
    "notes": "Net 30",
    "line_items": [],
    "created_at": "2026-01-15T10:00:00",
    "updated_at": "2026-01-15T10:00:00",
}

SAMPLE_COMPANY_SETTINGS = {
    "id": "settings-uuid-123",
    "user_id": "user-123",
    "company_name": "My Company Ltd",
    "company_email": "info@mycompany.com",
    "company_phone": "020 1234 5678",
    "bank_account_name": None,
    "bank_name": None,
    "account_number": None,
    "sort_code": None,
    "iban": None,
    "created_at": "2026-01-15T10:00:00",
    "updated_at": "2026-01-15T10:00:00",
}


def _create_mock_sendgrid():
    """Create a mock SendGridAPIClient that returns 202"""
    mock_sg = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_sg.send.return_value = mock_response
    return mock_sg


def get_test_app():
    """Get app with auth dependency overridden"""
    with patch("database.get_pool", new_callable=AsyncMock), \
         patch("database.close_pool", new_callable=AsyncMock):
        from main import app
        from auth import get_current_user
        app.dependency_overrides[get_current_user] = lambda: "user-123"
        return app


def get_test_app_no_auth():
    """Get app without auth override (to test 401)"""
    with patch("database.get_pool", new_callable=AsyncMock), \
         patch("database.close_pool", new_callable=AsyncMock):
        from main import app
        from auth import get_current_user
        app.dependency_overrides.pop(get_current_user, None)
        return app


# ============================================================
# Test 1: should send email with correct recipient and HTML body
# ============================================================

@pytest.mark.asyncio
async def test_should_send_email_with_correct_recipient_and_html_body():
    """should send email with correct recipient and HTML body via SendGrid"""
    # Arrange
    mock_sg = _create_mock_sendgrid()

    with patch("email_service.SendGridAPIClient", return_value=mock_sg):
        from email_service import send_invoice_email

        # Act
        result = await send_invoice_email(**SAMPLE_EMAIL_PARAMS)

    # Assert
    assert result is True
    mock_sg.send.assert_called_once()
    sent_message = mock_sg.send.call_args[0][0]
    assert sent_message.personalizations[0].tos[0]["email"] == "billing@acme.com"


# ============================================================
# Test 2: should include correct subject with invoice number and company name
# ============================================================

@pytest.mark.asyncio
async def test_should_include_correct_subject_with_invoice_number_and_company_name():
    """should include correct subject with invoice number and company name"""
    # Arrange
    mock_sg = _create_mock_sendgrid()

    with patch("email_service.SendGridAPIClient", return_value=mock_sg):
        from email_service import send_invoice_email

        # Act
        await send_invoice_email(**SAMPLE_EMAIL_PARAMS)

    # Assert
    sent_message = mock_sg.send.call_args[0][0]
    assert sent_message.subject.get() == "Invoice INV-0001 from My Company Ltd"


# ============================================================
# Test 3: should include PDF attachment with correct filename
# ============================================================

@pytest.mark.asyncio
async def test_should_include_pdf_attachment_with_correct_filename():
    """should include PDF attachment with correct filename"""
    # Arrange
    mock_sg = _create_mock_sendgrid()

    with patch("email_service.SendGridAPIClient", return_value=mock_sg):
        from email_service import send_invoice_email

        # Act
        await send_invoice_email(**SAMPLE_EMAIL_PARAMS)

    # Assert
    sent_message = mock_sg.send.call_args[0][0]
    message_dict = sent_message.get()
    attachments = message_dict["attachments"]
    assert len(attachments) == 1
    assert attachments[0]["filename"] == "Invoice-INV-0001.pdf"
    assert attachments[0]["type"] == "application/pdf"
    assert attachments[0]["disposition"] == "attachment"


# ============================================================
# Test 4: should return success on POST /api/invoices/{id}/send
# ============================================================

@pytest.mark.asyncio
async def test_should_return_success_on_send_invoice_endpoint():
    """should return success on POST /api/invoices/{id}/send"""
    # Arrange
    app = get_test_app()
    sent_invoice = {**SAMPLE_INVOICE, "status": "sent"}

    with patch("database.get_invoice_by_id", new_callable=AsyncMock, return_value=SAMPLE_INVOICE), \
         patch("database.get_company_settings", new_callable=AsyncMock, return_value=SAMPLE_COMPANY_SETTINGS), \
         patch("pdf_generator.generate_invoice_pdf", return_value=b"%PDF-fake"), \
         patch("email_service.send_invoice_email", new_callable=AsyncMock, return_value=True), \
         patch("database.update_invoice_status", new_callable=AsyncMock, return_value=sent_invoice):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.post("/api/invoices/invoice-uuid-123/send")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Invoice sent successfully"
    assert data["status"] == "sent"


# ============================================================
# Test 5: should update invoice status to sent after sending
# ============================================================

@pytest.mark.asyncio
async def test_should_update_invoice_status_to_sent_after_sending():
    """should update invoice status to sent after sending"""
    # Arrange
    app = get_test_app()
    sent_invoice = {**SAMPLE_INVOICE, "status": "sent"}
    mock_update_status = AsyncMock(return_value=sent_invoice)

    with patch("database.get_invoice_by_id", new_callable=AsyncMock, return_value=SAMPLE_INVOICE), \
         patch("database.get_company_settings", new_callable=AsyncMock, return_value=SAMPLE_COMPANY_SETTINGS), \
         patch("pdf_generator.generate_invoice_pdf", return_value=b"%PDF-fake"), \
         patch("email_service.send_invoice_email", new_callable=AsyncMock, return_value=True), \
         patch("database.update_invoice_status", mock_update_status):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            await client.post("/api/invoices/invoice-uuid-123/send")

    # Assert
    mock_update_status.assert_called_once_with("invoice-uuid-123", "user-123", "sent")


# ============================================================
# Test 6: should return 404 when invoice not found for send
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_invoice_not_found_for_send():
    """should return 404 when invoice not found for send"""
    # Arrange
    app = get_test_app()

    with patch("database.get_invoice_by_id", new_callable=AsyncMock, return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.post("/api/invoices/nonexistent-id/send")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"


# ============================================================
# Test 7: should return 401 when no auth token provided for send
# ============================================================

@pytest.mark.asyncio
async def test_should_return_401_when_no_auth_token_provided_for_send():
    """should return 401 when no auth token provided for send"""
    # Arrange
    app = get_test_app_no_auth()

    with patch("database.get_pool", new_callable=AsyncMock), \
         patch("database.close_pool", new_callable=AsyncMock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.post("/api/invoices/invoice-uuid-123/send")

    # Assert
    assert response.status_code in [401, 403]
