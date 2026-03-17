"""
Tests for Dashboard endpoints
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from datetime import datetime


# Sample dashboard stats data
SAMPLE_STATS = {
    "total_clients": 5,
    "total_invoices": 12,
    "total_revenue": 15000.00,
    "outstanding_amount": 3500.00,
    "overdue_count": 2,
    "paid_this_month": 5000.00,
    "draft_count": 3,
    "recent_invoices": [
        {
            "id": "inv-1",
            "invoice_number": "INV-0001",
            "client_name": "Acme Corp",
            "total_due": 1200.00,
            "status": "paid",
            "created_at": "2026-03-01T10:00:00",
        },
        {
            "id": "inv-2",
            "invoice_number": "INV-0002",
            "client_name": "Beta Inc",
            "total_due": 500.00,
            "status": "sent",
            "created_at": "2026-03-05T10:00:00",
        },
    ],
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
# Test 1: GET /api/dashboard - returns stats with correct fields
# ============================================================

@pytest.mark.asyncio
async def test_should_return_dashboard_stats_with_correct_fields():
    """should return dashboard stats with correct fields on GET /api/dashboard"""
    # Arrange
    app = get_test_app()
    with patch("database.get_dashboard_stats", new_callable=AsyncMock, return_value=SAMPLE_STATS):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/dashboard")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total_invoices"] == 12
    assert data["total_revenue"] == 15000.00
    assert data["outstanding_amount"] == 3500.00
    assert data["overdue_count"] == 2
    assert data["draft_count"] == 3
    assert len(data["recent_invoices"]) == 2
    assert data["recent_invoices"][0]["invoice_number"] == "INV-0001"


# ============================================================
# Test 2: GET /api/dashboard - returns zero values when no invoices
# ============================================================

EMPTY_STATS = {
    "total_clients": 0,
    "total_invoices": 0,
    "total_revenue": 0.0,
    "outstanding_amount": 0.0,
    "overdue_count": 0,
    "paid_this_month": 0.0,
    "draft_count": 0,
    "recent_invoices": [],
}


@pytest.mark.asyncio
async def test_should_return_zero_values_when_user_has_no_invoices():
    """should return zero values when user has no invoices"""
    # Arrange
    app = get_test_app()
    with patch("database.get_dashboard_stats", new_callable=AsyncMock, return_value=EMPTY_STATS):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/dashboard")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total_clients"] == 0
    assert data["total_invoices"] == 0
    assert data["total_revenue"] == 0.0
    assert data["outstanding_amount"] == 0.0
    assert data["overdue_count"] == 0
    assert data["draft_count"] == 0
    assert data["recent_invoices"] == []


# ============================================================
# Test 3: GET /api/dashboard - 401 without auth
# ============================================================

@pytest.mark.asyncio
async def test_should_return_401_when_no_auth_token_provided():
    """should return 401 when no auth token provided on GET /api/dashboard"""
    # Arrange
    app = get_test_app_no_auth()
    with patch("database.get_pool", new_callable=AsyncMock), \
         patch("database.close_pool", new_callable=AsyncMock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act - no Authorization header
            response = await client.get("/api/dashboard")

    # Assert
    assert response.status_code in [401, 403]
