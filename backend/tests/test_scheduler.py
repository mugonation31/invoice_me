"""
Tests for the scheduler module - processing due schedules
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import date, datetime


# Sample schedule data
SAMPLE_DUE_SCHEDULE = {
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
    "next_run_date": date(2026, 3, 17),
    "auto_send": False,
    "active": True,
    "created_at": datetime(2026, 1, 1, 10, 0, 0),
    "updated_at": datetime(2026, 3, 1, 10, 0, 0),
}

SAMPLE_INVOICE_RESULT = {
    "id": "inv-uuid-new",
    "user_id": "user-123",
    "client_id": "client-uuid-123",
    "client_name": "Acme Corp",
    "client_email": "billing@acme.com",
    "invoice_number": "INV-0010",
    "status": "draft",
    "issue_date": "2026-03-17",
    "due_date": "2026-04-16",
    "subtotal": 5000.0,
    "tax_rate": 10.0,
    "tax_amount": 500.0,
    "total_due": 5500.0,
    "notes": None,
    "line_items": [],
    "created_at": "2026-03-17T10:00:00",
    "updated_at": "2026-03-17T10:00:00",
}


# ============================================================
# Test 9: should find due schedules
# ============================================================

@pytest.mark.asyncio
async def test_should_find_due_schedules():
    """should find due schedules where next_run_date <= today"""
    # Arrange
    from scheduler import process_due_schedules

    mock_due_schedules = [SAMPLE_DUE_SCHEDULE]

    with patch("scheduler.db.get_due_schedules", new_callable=AsyncMock,
               return_value=mock_due_schedules) as mock_get_due, \
         patch("scheduler.db.create_invoice", new_callable=AsyncMock,
               return_value=SAMPLE_INVOICE_RESULT), \
         patch("scheduler.db.advance_schedule_date", new_callable=AsyncMock):

        # Act
        await process_due_schedules()

        # Assert
        mock_get_due.assert_called_once()


# ============================================================
# Test 10: should create invoice from schedule template
# ============================================================

@pytest.mark.asyncio
async def test_should_create_invoice_from_schedule_template():
    """should create invoice from schedule template when processing due schedules"""
    # Arrange
    from scheduler import process_due_schedules

    with patch("scheduler.db.get_due_schedules", new_callable=AsyncMock,
               return_value=[SAMPLE_DUE_SCHEDULE]) as mock_get_due, \
         patch("scheduler.db.create_invoice", new_callable=AsyncMock,
               return_value=SAMPLE_INVOICE_RESULT) as mock_create_invoice, \
         patch("scheduler.db.advance_schedule_date", new_callable=AsyncMock):

        # Act
        await process_due_schedules()

        # Assert
        mock_create_invoice.assert_called_once()
        call_args = mock_create_invoice.call_args
        assert call_args[0][0] == "user-123"  # user_id
        invoice_data = call_args[0][1]
        assert invoice_data.client_id == "client-uuid-123"
        assert invoice_data.tax_rate == 10.0
        assert len(invoice_data.line_items) == 1
        assert invoice_data.line_items[0].description == "Monthly Retainer"


# ============================================================
# Test 11: should advance next_run_date for monthly recurrence
# ============================================================

@pytest.mark.asyncio
async def test_should_advance_next_run_date_for_monthly_recurrence():
    """should advance next_run_date for monthly recurrence after processing"""
    # Arrange
    from scheduler import process_due_schedules

    with patch("scheduler.db.get_due_schedules", new_callable=AsyncMock,
               return_value=[SAMPLE_DUE_SCHEDULE]), \
         patch("scheduler.db.create_invoice", new_callable=AsyncMock,
               return_value=SAMPLE_INVOICE_RESULT), \
         patch("scheduler.db.advance_schedule_date", new_callable=AsyncMock) as mock_advance:

        # Act
        await process_due_schedules()

        # Assert
        mock_advance.assert_called_once_with("sched-uuid-123", "monthly")


# ============================================================
# Test 12: should deactivate schedule with 'once' recurrence
# ============================================================

@pytest.mark.asyncio
async def test_should_deactivate_schedule_with_once_recurrence():
    """should deactivate schedule with 'once' recurrence after processing"""
    # Arrange
    from scheduler import process_due_schedules

    once_schedule = {**SAMPLE_DUE_SCHEDULE, "recurrence": "once"}

    with patch("scheduler.db.get_due_schedules", new_callable=AsyncMock,
               return_value=[once_schedule]), \
         patch("scheduler.db.create_invoice", new_callable=AsyncMock,
               return_value=SAMPLE_INVOICE_RESULT), \
         patch("scheduler.db.advance_schedule_date", new_callable=AsyncMock) as mock_advance:

        # Act
        await process_due_schedules()

        # Assert
        mock_advance.assert_called_once_with("sched-uuid-123", "once")
