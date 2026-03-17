"""
Tests for Invoice CRUD endpoints
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from datetime import datetime, date


# Sample data for tests
SAMPLE_LINE_ITEM = {
    "id": "line-uuid-001",
    "invoice_id": "invoice-uuid-123",
    "description": "Web Development",
    "quantity": 10.0,
    "rate": 150.0,
    "amount": 1500.0,
    "sort_order": 0,
    "created_at": "2026-01-15T10:00:00",
}

SAMPLE_LINE_ITEM_2 = {
    "id": "line-uuid-002",
    "invoice_id": "invoice-uuid-123",
    "description": "Design Work",
    "quantity": 5.0,
    "rate": 100.0,
    "amount": 500.0,
    "sort_order": 1,
    "created_at": "2026-01-15T10:00:00",
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
    "line_items": [SAMPLE_LINE_ITEM, SAMPLE_LINE_ITEM_2],
    "created_at": "2026-01-15T10:00:00",
    "updated_at": "2026-01-15T10:00:00",
}

SAMPLE_INVOICE_LIST_ITEM = {
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
# Test 1: GET /api/invoices - empty list
# ============================================================

@pytest.mark.asyncio
async def test_should_return_empty_list_when_user_has_no_invoices():
    """should return empty list when user has no invoices on GET /api/invoices"""
    # Arrange
    app = get_test_app()
    with patch("database.get_invoices", new_callable=AsyncMock, return_value=[]):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/invoices")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


# ============================================================
# Test 2: POST /api/invoices - create with line items
# ============================================================

@pytest.mark.asyncio
async def test_should_return_201_and_created_invoice_with_calculated_totals():
    """should return 201 and created invoice with calculated totals on POST /api/invoices"""
    # Arrange
    app = get_test_app()
    create_data = {
        "client_id": "client-uuid-123",
        "issue_date": "2026-01-15",
        "due_date": "2026-02-15",
        "tax_rate": 10.0,
        "notes": "Net 30",
        "line_items": [
            {"description": "Web Development", "quantity": 10, "rate": 150.0},
            {"description": "Design Work", "quantity": 5, "rate": 100.0},
        ],
    }
    with patch("database.create_invoice", new_callable=AsyncMock, return_value=SAMPLE_INVOICE):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.post("/api/invoices", json=create_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["invoice_number"] == "INV-0001"
    assert data["subtotal"] == 2000.0
    assert data["tax_rate"] == 10.0
    assert data["tax_amount"] == 200.0
    assert data["total_due"] == 2200.0
    assert data["status"] == "draft"
    assert len(data["line_items"]) == 2
    assert data["line_items"][0]["description"] == "Web Development"
    assert data["line_items"][0]["amount"] == 1500.0


# ============================================================
# Test 3: GET /api/invoices - returns invoice list with client_name
# ============================================================

@pytest.mark.asyncio
async def test_should_return_invoice_list_with_client_name_when_invoices_exist():
    """should return invoice list with client_name on GET /api/invoices"""
    # Arrange
    app = get_test_app()
    second_invoice = {
        **SAMPLE_INVOICE_LIST_ITEM,
        "id": "invoice-uuid-456",
        "invoice_number": "INV-0002",
        "client_name": "Beta Inc",
    }
    with patch("database.get_invoices", new_callable=AsyncMock,
               return_value=[SAMPLE_INVOICE_LIST_ITEM, second_invoice]):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/invoices")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["client_name"] == "Acme Corp"
    assert data[1]["client_name"] == "Beta Inc"
    assert data[0]["line_items"] == []


# ============================================================
# Test 4: GET /api/invoices/{id} - single invoice with line items
# ============================================================

@pytest.mark.asyncio
async def test_should_return_single_invoice_with_line_items_on_get_by_id():
    """should return single invoice with line items on GET /api/invoices/{id}"""
    # Arrange
    app = get_test_app()
    with patch("database.get_invoice_by_id", new_callable=AsyncMock,
               return_value=SAMPLE_INVOICE):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/invoices/invoice-uuid-123")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "invoice-uuid-123"
    assert data["invoice_number"] == "INV-0001"
    assert data["client_name"] == "Acme Corp"
    assert data["client_email"] == "billing@acme.com"
    assert len(data["line_items"]) == 2
    assert data["line_items"][0]["rate"] == 150.0
    assert data["line_items"][1]["amount"] == 500.0


# ============================================================
# Test 5: GET /api/invoices/{id} - not found
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_invoice_not_found_on_get():
    """should return 404 on GET /api/invoices/{id} when invoice not found"""
    # Arrange
    app = get_test_app()
    with patch("database.get_invoice_by_id", new_callable=AsyncMock, return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/invoices/nonexistent-id")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"


# ============================================================
# Test 6: PATCH /api/invoices/{id} - update invoice
# ============================================================

@pytest.mark.asyncio
async def test_should_return_updated_invoice_on_patch():
    """should return updated invoice on PATCH /api/invoices/{id}"""
    # Arrange
    app = get_test_app()
    updated_invoice = {**SAMPLE_INVOICE, "notes": "Updated notes", "status": "sent"}
    with patch("database.update_invoice", new_callable=AsyncMock,
               return_value=updated_invoice):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.patch(
                "/api/invoices/invoice-uuid-123",
                json={"notes": "Updated notes", "status": "sent"}
            )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "Updated notes"
    assert data["status"] == "sent"


# ============================================================
# Test 7: PATCH /api/invoices/{id} - not found
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_invoice_not_found_on_patch():
    """should return 404 on PATCH /api/invoices/{id} when invoice not found"""
    # Arrange
    app = get_test_app()
    with patch("database.update_invoice", new_callable=AsyncMock, return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.patch(
                "/api/invoices/nonexistent-id",
                json={"notes": "Updated"}
            )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"


# ============================================================
# Test 8: DELETE /api/invoices/{id} - success
# ============================================================

@pytest.mark.asyncio
async def test_should_return_success_message_on_delete():
    """should return success message on DELETE /api/invoices/{id}"""
    # Arrange
    app = get_test_app()
    with patch("database.delete_invoice", new_callable=AsyncMock, return_value=True):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.delete("/api/invoices/invoice-uuid-123")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Invoice deleted successfully"


# ============================================================
# Test 9: DELETE /api/invoices/{id} - not found
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_invoice_not_found_on_delete():
    """should return 404 on DELETE /api/invoices/{id} when invoice not found"""
    # Arrange
    app = get_test_app()
    with patch("database.delete_invoice", new_callable=AsyncMock, return_value=False):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.delete("/api/invoices/nonexistent-id")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"


# ============================================================
# Test 10: PATCH /api/invoices/{id}/status - update status
# ============================================================

@pytest.mark.asyncio
async def test_should_update_invoice_status_on_patch_status():
    """should update invoice status on PATCH /api/invoices/{id}/status"""
    # Arrange
    app = get_test_app()
    status_updated_invoice = {**SAMPLE_INVOICE, "status": "sent"}
    with patch("database.update_invoice_status", new_callable=AsyncMock,
               return_value=status_updated_invoice):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.patch(
                "/api/invoices/invoice-uuid-123/status",
                json={"status": "sent"}
            )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"


# ============================================================
# Test 11: PATCH /api/invoices/{id}/status - not found
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_invoice_not_found_on_status_update():
    """should return 404 on PATCH /api/invoices/{id}/status when invoice not found"""
    # Arrange
    app = get_test_app()
    with patch("database.update_invoice_status", new_callable=AsyncMock,
               return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.patch(
                "/api/invoices/nonexistent-id/status",
                json={"status": "paid"}
            )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Invoice not found"


# ============================================================
# Test 12: GET /api/invoices - 401 without auth
# ============================================================

@pytest.mark.asyncio
async def test_should_return_401_when_no_auth_token_provided_for_invoices():
    """should return 401 when no auth token provided for invoice endpoints"""
    # Arrange
    app = get_test_app_no_auth()
    with patch("database.get_pool", new_callable=AsyncMock), \
         patch("database.close_pool", new_callable=AsyncMock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act - no Authorization header
            response = await client.get("/api/invoices")

    # Assert
    assert response.status_code in [401, 403]
