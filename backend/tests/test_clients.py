"""
Tests for Client CRUD endpoints
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from datetime import datetime


# Sample client data for tests
SAMPLE_CLIENT = {
    "id": "client-uuid-123",
    "user_id": "user-123",
    "name": "Acme Corp",
    "email": "billing@acme.com",
    "phone": "555-0100",
    "address": "123 Main St",
    "created_at": "2026-01-15T10:00:00",
    "updated_at": "2026-01-15T10:00:00",
}

SAMPLE_CLIENT_2 = {
    "id": "client-uuid-456",
    "user_id": "user-123",
    "name": "Beta Inc",
    "email": "info@beta.com",
    "phone": None,
    "address": None,
    "created_at": "2026-01-16T10:00:00",
    "updated_at": "2026-01-16T10:00:00",
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
        # Remove any existing overrides
        app.dependency_overrides.pop(get_current_user, None)
        return app


# ============================================================
# Test 1: GET /api/clients - empty list
# ============================================================

@pytest.mark.asyncio
async def test_should_return_empty_list_when_user_has_no_clients():
    """should return empty list when user has no clients on GET /api/clients"""
    # Arrange
    app = get_test_app()
    with patch("database.get_clients", new_callable=AsyncMock, return_value=[]):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/clients")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


# ============================================================
# Test 2: POST /api/clients - create client
# ============================================================

@pytest.mark.asyncio
async def test_should_return_201_and_created_client_on_post():
    """should return 201 and created client on POST /api/clients"""
    # Arrange
    app = get_test_app()
    create_data = {"name": "Acme Corp", "email": "billing@acme.com"}
    with patch("database.create_client", new_callable=AsyncMock, return_value=SAMPLE_CLIENT):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.post("/api/clients", json=create_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Acme Corp"
    assert data["email"] == "billing@acme.com"
    assert data["id"] == "client-uuid-123"


# ============================================================
# Test 3: GET /api/clients - returns client list
# ============================================================

@pytest.mark.asyncio
async def test_should_return_client_list_when_clients_exist():
    """should return client list on GET /api/clients when clients exist"""
    # Arrange
    app = get_test_app()
    with patch("database.get_clients", new_callable=AsyncMock, return_value=[SAMPLE_CLIENT, SAMPLE_CLIENT_2]):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/clients")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Acme Corp"
    assert data[1]["name"] == "Beta Inc"


# ============================================================
# Test 4: GET /api/clients/{id} - single client
# ============================================================

@pytest.mark.asyncio
async def test_should_return_single_client_on_get_by_id():
    """should return single client on GET /api/clients/{id}"""
    # Arrange
    app = get_test_app()
    with patch("database.get_client_by_id", new_callable=AsyncMock, return_value=SAMPLE_CLIENT):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/clients/client-uuid-123")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "client-uuid-123"
    assert data["name"] == "Acme Corp"


# ============================================================
# Test 5: GET /api/clients/{id} - not found
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_client_not_found_on_get():
    """should return 404 on GET /api/clients/{id} when client not found"""
    # Arrange
    app = get_test_app()
    with patch("database.get_client_by_id", new_callable=AsyncMock, return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/clients/nonexistent-id")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found"


# ============================================================
# Test 6: PATCH /api/clients/{id} - update client
# ============================================================

@pytest.mark.asyncio
async def test_should_return_updated_client_on_patch():
    """should return updated client on PATCH /api/clients/{id}"""
    # Arrange
    app = get_test_app()
    updated_client = {**SAMPLE_CLIENT, "name": "Acme Corporation"}
    with patch("database.update_client", new_callable=AsyncMock, return_value=updated_client):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.patch(
                "/api/clients/client-uuid-123",
                json={"name": "Acme Corporation"}
            )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Acme Corporation"


# ============================================================
# Test 7: PATCH /api/clients/{id} - not found
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_client_not_found_on_patch():
    """should return 404 on PATCH /api/clients/{id} when client not found"""
    # Arrange
    app = get_test_app()
    with patch("database.update_client", new_callable=AsyncMock, return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.patch(
                "/api/clients/nonexistent-id",
                json={"name": "Updated Name"}
            )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found"


# ============================================================
# Test 8: DELETE /api/clients/{id} - success
# ============================================================

@pytest.mark.asyncio
async def test_should_return_success_message_on_delete():
    """should return success message on DELETE /api/clients/{id}"""
    # Arrange
    app = get_test_app()
    with patch("database.delete_client", new_callable=AsyncMock, return_value=True):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.delete("/api/clients/client-uuid-123")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Client deleted successfully"


# ============================================================
# Test 9: DELETE /api/clients/{id} - not found
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_client_not_found_on_delete():
    """should return 404 on DELETE /api/clients/{id} when client not found"""
    # Arrange
    app = get_test_app()
    with patch("database.delete_client", new_callable=AsyncMock, return_value=False):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.delete("/api/clients/nonexistent-id")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found"


# ============================================================
# Test 10: GET /api/clients - 401 without auth
# ============================================================

@pytest.mark.asyncio
async def test_should_return_401_when_no_auth_token_provided():
    """should return 401 when no auth token provided"""
    # Arrange
    app = get_test_app_no_auth()
    with patch("database.get_pool", new_callable=AsyncMock), \
         patch("database.close_pool", new_callable=AsyncMock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act - no Authorization header
            response = await client.get("/api/clients")

    # Assert
    assert response.status_code in [401, 403]
