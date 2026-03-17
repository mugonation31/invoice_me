"""
Tests for Schedule CRUD endpoints
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from datetime import datetime, date


# Sample schedule data for tests
SAMPLE_SCHEDULE = {
    "id": "sched-uuid-123",
    "user_id": "user-123",
    "client_id": "client-uuid-123",
    "client_name": "Acme Corp",
    "description": "Monthly retainer",
    "line_items": [
        {"description": "Monthly Retainer", "quantity": 1, "rate": 5000.00},
    ],
    "tax_rate": 10.0,
    "recurrence": "monthly",
    "next_run_date": "2026-04-01",
    "auto_send": False,
    "active": True,
    "created_at": "2026-03-01T10:00:00",
    "updated_at": "2026-03-01T10:00:00",
}

SAMPLE_SCHEDULE_2 = {
    **SAMPLE_SCHEDULE,
    "id": "sched-uuid-456",
    "client_name": "Beta Inc",
    "description": "Weekly consulting",
    "recurrence": "weekly",
    "next_run_date": "2026-03-20",
}


def get_test_app():
    """Get app with auth dependency overridden"""
    with patch("database.get_pool", new_callable=AsyncMock), \
         patch("database.close_pool", new_callable=AsyncMock):
        from main import app
        from auth import get_current_user
        app.dependency_overrides[get_current_user] = lambda: "user-123"
        return app


# ============================================================
# Test 1: GET /api/schedules - empty list
# ============================================================

@pytest.mark.asyncio
async def test_should_return_empty_list_when_user_has_no_schedules():
    """should return empty list when user has no schedules on GET /api/schedules"""
    # Arrange
    app = get_test_app()
    with patch("database.get_schedules", new_callable=AsyncMock, return_value=[]):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/schedules")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


# ============================================================
# Test 2: POST /api/schedules - create schedule
# ============================================================

@pytest.mark.asyncio
async def test_should_return_201_and_created_schedule_on_post():
    """should return 201 and created schedule on POST /api/schedules"""
    # Arrange
    app = get_test_app()
    create_data = {
        "client_id": "client-uuid-123",
        "description": "Monthly retainer",
        "recurrence": "monthly",
        "next_run_date": "2026-04-01",
        "tax_rate": 10.0,
        "auto_send": False,
        "line_items": [
            {"description": "Monthly Retainer", "quantity": 1, "rate": 5000.00},
        ],
    }
    with patch("database.create_schedule", new_callable=AsyncMock, return_value=SAMPLE_SCHEDULE):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.post("/api/schedules", json=create_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "sched-uuid-123"
    assert data["recurrence"] == "monthly"
    assert data["client_name"] == "Acme Corp"
    assert data["next_run_date"] == "2026-04-01"


# ============================================================
# Test 3: GET /api/schedules - returns schedule list
# ============================================================

@pytest.mark.asyncio
async def test_should_return_schedule_list_when_schedules_exist():
    """should return schedule list on GET /api/schedules when schedules exist"""
    # Arrange
    app = get_test_app()
    with patch("database.get_schedules", new_callable=AsyncMock,
               return_value=[SAMPLE_SCHEDULE, SAMPLE_SCHEDULE_2]):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/schedules")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["client_name"] == "Acme Corp"
    assert data[1]["recurrence"] == "weekly"


# ============================================================
# Test 4: GET /api/schedules/{id} - single schedule
# ============================================================

@pytest.mark.asyncio
async def test_should_return_single_schedule_on_get_by_id():
    """should return single schedule on GET /api/schedules/{id}"""
    # Arrange
    app = get_test_app()
    with patch("database.get_schedule_by_id", new_callable=AsyncMock, return_value=SAMPLE_SCHEDULE):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/schedules/sched-uuid-123")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "sched-uuid-123"
    assert data["description"] == "Monthly retainer"


# ============================================================
# Test 5: GET /api/schedules/{id} - not found
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_schedule_not_found_on_get():
    """should return 404 on GET /api/schedules/{id} when schedule not found"""
    # Arrange
    app = get_test_app()
    with patch("database.get_schedule_by_id", new_callable=AsyncMock, return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.get("/api/schedules/nonexistent-id")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Schedule not found"


# ============================================================
# Test 6: PATCH /api/schedules/{id} - update schedule
# ============================================================

@pytest.mark.asyncio
async def test_should_return_updated_schedule_on_patch():
    """should return updated schedule on PATCH /api/schedules/{id}"""
    # Arrange
    app = get_test_app()
    updated_schedule = {**SAMPLE_SCHEDULE, "description": "Updated retainer", "active": False}
    with patch("database.update_schedule", new_callable=AsyncMock, return_value=updated_schedule):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.patch(
                "/api/schedules/sched-uuid-123",
                json={"description": "Updated retainer", "active": False}
            )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated retainer"
    assert data["active"] is False


# ============================================================
# Test 7: DELETE /api/schedules/{id} - success
# ============================================================

@pytest.mark.asyncio
async def test_should_return_success_message_on_delete():
    """should return success message on DELETE /api/schedules/{id}"""
    # Arrange
    app = get_test_app()
    with patch("database.delete_schedule", new_callable=AsyncMock, return_value=True):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.delete("/api/schedules/sched-uuid-123")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Schedule deleted successfully"


# ============================================================
# Test 8: DELETE /api/schedules/{id} - not found
# ============================================================

@pytest.mark.asyncio
async def test_should_return_404_when_schedule_not_found_on_delete():
    """should return 404 on DELETE /api/schedules/{id} when schedule not found"""
    # Arrange
    app = get_test_app()
    with patch("database.delete_schedule", new_callable=AsyncMock, return_value=False):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Act
            response = await client.delete("/api/schedules/nonexistent-id")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Schedule not found"
