"""
Tests for Invoice PDF generation
"""
import pytest
from io import BytesIO
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
import pdfplumber


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Helper to extract all text from PDF bytes"""
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


# Sample data for PDF tests
SAMPLE_LINE_ITEMS = [
    {
        "description": "Web Development",
        "quantity": 10.0,
        "rate": 150.0,
        "amount": 1500.0,
    },
    {
        "description": "Design Work",
        "quantity": 5.0,
        "rate": 100.0,
        "amount": 500.0,
    },
]

SAMPLE_INVOICE = {
    "id": "invoice-uuid-123",
    "user_id": "user-123",
    "client_id": "client-uuid-123",
    "client_name": "Acme Corp",
    "client_email": "billing@acme.com",
    "client_address": "123 Main St, London",
    "invoice_number": "INV-0001",
    "status": "draft",
    "issue_date": "2026-01-15",
    "due_date": "2026-02-15",
    "subtotal": 2000.0,
    "tax_rate": 10.0,
    "tax_amount": 200.0,
    "total_due": 2200.0,
    "notes": "Net 30",
    "line_items": SAMPLE_LINE_ITEMS,
}

SAMPLE_COMPANY_SETTINGS = {
    "company_name": "My Company Ltd",
    "company_email": "info@mycompany.com",
    "company_phone": "+44 7700 900000",
    "bank_account_name": "My Company Ltd",
    "bank_name": "Barclays Bank",
    "account_number": "12345678",
    "sort_code": "20-00-00",
    "iban": "GB29NWBK60161331926819",
}


# ============================================================
# Test 1: should generate PDF bytes from invoice data
# ============================================================

def test_should_generate_pdf_bytes_from_invoice_data():
    """should generate PDF bytes from invoice data"""
    # Arrange
    from pdf_generator import generate_invoice_pdf

    # Act
    result = generate_invoice_pdf(SAMPLE_INVOICE, SAMPLE_COMPANY_SETTINGS)

    # Assert
    assert isinstance(result, bytes)
    assert len(result) > 0
    # PDF files start with %PDF
    assert result[:5] == b"%PDF-"


# ============================================================
# Test 2: should include invoice number in PDF
# ============================================================

def test_should_include_invoice_number_in_pdf():
    """should include invoice number in PDF"""
    # Arrange
    from pdf_generator import generate_invoice_pdf

    # Act
    result = generate_invoice_pdf(SAMPLE_INVOICE, SAMPLE_COMPANY_SETTINGS)

    # Assert
    pdf_text = extract_pdf_text(result)
    assert "INV-0001" in pdf_text


# ============================================================
# Test 3: should include line items in PDF
# ============================================================

def test_should_include_line_items_in_pdf():
    """should include line items in PDF"""
    # Arrange
    from pdf_generator import generate_invoice_pdf

    # Act
    result = generate_invoice_pdf(SAMPLE_INVOICE, SAMPLE_COMPANY_SETTINGS)

    # Assert
    pdf_text = extract_pdf_text(result)
    assert "Web Development" in pdf_text
    assert "Design Work" in pdf_text
    assert "1500.00" in pdf_text
    assert "500.00" in pdf_text


# ============================================================
# Test 4: should include company name in PDF
# ============================================================

def test_should_include_company_name_in_pdf():
    """should include company name in PDF"""
    # Arrange
    from pdf_generator import generate_invoice_pdf

    # Act
    result = generate_invoice_pdf(SAMPLE_INVOICE, SAMPLE_COMPANY_SETTINGS)

    # Assert
    pdf_text = extract_pdf_text(result)
    assert "My Company Ltd" in pdf_text
    assert "info@mycompany.com" in pdf_text


# ============================================================
# Test 5: should include payment details in PDF
# ============================================================

def test_should_include_payment_details_in_pdf():
    """should include payment details in PDF"""
    # Arrange
    from pdf_generator import generate_invoice_pdf

    # Act
    result = generate_invoice_pdf(SAMPLE_INVOICE, SAMPLE_COMPANY_SETTINGS)

    # Assert
    pdf_text = extract_pdf_text(result)
    assert "PAYMENT DETAILS" in pdf_text
    assert "Barclays Bank" in pdf_text
    assert "12345678" in pdf_text
    assert "20-00-00" in pdf_text
    assert "GB29NWBK60161331926819" in pdf_text


# ============================================================
# Test helpers for endpoint tests
# ============================================================

def get_test_app():
    """Get app with auth dependency overridden"""
    with patch("database.get_pool", new_callable=AsyncMock), \
         patch("database.close_pool", new_callable=AsyncMock):
        from main import app
        from auth import get_current_user
        app.dependency_overrides[get_current_user] = lambda: "user-123"
        return app


# ============================================================
# Test 6: should return PDF on GET /api/invoices/{id}/pdf
# ============================================================

@pytest.mark.asyncio
async def test_should_return_pdf_on_get_invoice_pdf_endpoint():
    """should return PDF on GET /api/invoices/{id}/pdf"""
    # Arrange
    app = get_test_app()
    with patch("database.get_invoice_by_id", new_callable=AsyncMock, return_value=SAMPLE_INVOICE), \
         patch("database.get_company_settings", new_callable=AsyncMock, return_value=SAMPLE_COMPANY_SETTINGS):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/invoices/invoice-uuid-123/pdf")

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers.get("content-disposition", "")
    assert response.content[:5] == b"%PDF-"


# ============================================================
# Test 7: should return 404 when invoice not found for PDF
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_invoice_not_found_for_pdf():
    """should return 404 when invoice not found for PDF"""
    # Arrange
    app = get_test_app()
    with patch("database.get_invoice_by_id", new_callable=AsyncMock, return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/invoices/nonexistent-id/pdf")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"
