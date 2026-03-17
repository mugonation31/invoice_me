"""
Tests for Pydantic models
"""
import pytest
from datetime import datetime


def test_should_create_valid_client_create_model_with_required_fields():
    """should create a valid ClientCreate model with required fields"""
    # Arrange
    data = {
        "name": "Acme Corp",
        "email": "billing@acme.com",
    }

    # Act
    from models import ClientCreate
    client = ClientCreate(**data)

    # Assert
    assert client.name == "Acme Corp"
    assert client.email == "billing@acme.com"
    assert client.phone is None
    assert client.address is None


def test_should_create_valid_client_update_model_with_all_optional_fields():
    """should create a valid ClientUpdate model with all optional fields"""
    # Arrange / Act
    from models import ClientUpdate
    client = ClientUpdate()

    # Assert - all fields should be None (optional)
    assert client.name is None
    assert client.email is None
    assert client.phone is None
    assert client.address is None


def test_should_create_valid_client_response_model_with_all_fields():
    """should create a valid ClientResponse model with all fields"""
    # Arrange
    now = datetime.utcnow()
    data = {
        "id": "uuid-123",
        "user_id": "user-456",
        "name": "Acme Corp",
        "email": "billing@acme.com",
        "phone": "555-0100",
        "address": "123 Main St",
        "created_at": now,
        "updated_at": now,
    }

    # Act
    from models import ClientResponse
    client = ClientResponse(**data)

    # Assert
    assert client.id == "uuid-123"
    assert client.user_id == "user-456"
    assert client.name == "Acme Corp"
    assert client.email == "billing@acme.com"
    assert client.created_at == now


def test_should_create_valid_invoice_status_enum_with_correct_values():
    """should create a valid InvoiceStatus enum with correct values"""
    # Act
    from models import InvoiceStatus

    # Assert
    assert InvoiceStatus.DRAFT == "draft"
    assert InvoiceStatus.SENT == "sent"
    assert InvoiceStatus.PAID == "paid"
    assert InvoiceStatus.OVERDUE == "overdue"
    assert len(InvoiceStatus) == 4


def test_should_create_valid_line_item_create_model_with_required_fields():
    """should create a valid LineItemCreate model with required fields"""
    # Arrange
    data = {
        "description": "Web Development",
        "quantity": 10.0,
        "rate": 150.00,
    }

    # Act
    from models import LineItemCreate
    item = LineItemCreate(**data)

    # Assert
    assert item.description == "Web Development"
    assert item.quantity == 10.0
    assert item.rate == 150.00


def test_should_create_valid_line_item_response_model_with_all_fields():
    """should create a valid LineItemResponse model with all fields"""
    # Arrange
    now = datetime.utcnow()
    data = {
        "id": "item-123",
        "invoice_id": "inv-456",
        "description": "Web Development",
        "quantity": 10.0,
        "rate": 150.00,
        "amount": 1500.00,
        "sort_order": 0,
        "created_at": now,
    }

    # Act
    from models import LineItemResponse
    item = LineItemResponse(**data)

    # Assert
    assert item.id == "item-123"
    assert item.invoice_id == "inv-456"
    assert item.amount == 1500.00
    assert item.sort_order == 0


def test_should_create_valid_invoice_create_model_with_nested_line_items():
    """should create a valid InvoiceCreate model with nested line items"""
    # Arrange
    data = {
        "client_id": "client-123",
        "due_date": "2026-04-01",
        "tax_rate": 10.0,
        "line_items": [
            {"description": "Web Dev", "quantity": 10, "rate": 150.00},
            {"description": "Design", "quantity": 5, "rate": 100.00},
        ],
        "notes": "Payment due within 30 days",
    }

    # Act
    from models import InvoiceCreate
    invoice = InvoiceCreate(**data)

    # Assert
    assert invoice.client_id == "client-123"
    assert invoice.tax_rate == 10.0
    assert len(invoice.line_items) == 2
    assert invoice.line_items[0].description == "Web Dev"
    assert invoice.notes == "Payment due within 30 days"


def test_should_create_valid_invoice_response_model_with_nested_line_items():
    """should create a valid InvoiceResponse model with nested line items and computed fields"""
    # Arrange
    now = datetime.utcnow()
    data = {
        "id": "inv-123",
        "user_id": "user-456",
        "client_id": "client-789",
        "client_name": "Acme Corp",
        "client_email": "billing@acme.com",
        "invoice_number": "INV-001",
        "status": "draft",
        "issue_date": "2026-01-15",
        "due_date": "2026-02-15",
        "subtotal": 2000.00,
        "tax_rate": 10.0,
        "tax_amount": 200.00,
        "total_due": 2200.00,
        "notes": "Net 30",
        "line_items": [
            {
                "id": "item-1",
                "invoice_id": "inv-123",
                "description": "Web Dev",
                "quantity": 10,
                "rate": 150.00,
                "amount": 1500.00,
                "sort_order": 0,
                "created_at": now,
            },
        ],
        "created_at": now,
        "updated_at": now,
    }

    # Act
    from models import InvoiceResponse
    invoice = InvoiceResponse(**data)

    # Assert
    assert invoice.id == "inv-123"
    assert invoice.invoice_number == "INV-001"
    assert invoice.status == "draft"
    assert invoice.total_due == 2200.00
    assert invoice.client_name == "Acme Corp"
    assert invoice.client_email == "billing@acme.com"
    assert len(invoice.line_items) == 1
    assert invoice.line_items[0].amount == 1500.00


def test_should_create_valid_schedule_create_model_with_required_fields():
    """should create a valid ScheduleCreate model with required fields"""
    # Arrange
    data = {
        "client_id": "client-123",
        "recurrence": "monthly",
        "next_run_date": "2026-04-01",
        "line_items": [
            {"description": "Monthly Retainer", "quantity": 1, "rate": 5000.00},
        ],
    }

    # Act
    from models import ScheduleCreate
    schedule = ScheduleCreate(**data)

    # Assert
    assert schedule.client_id == "client-123"
    assert schedule.recurrence == "monthly"
    assert schedule.tax_rate == 0
    assert schedule.auto_send is False
    assert schedule.description is None
    assert len(schedule.line_items) == 1


def test_should_create_valid_schedule_response_model():
    """should create a valid ScheduleResponse model"""
    # Arrange
    now = datetime.utcnow()
    data = {
        "id": "sched-123",
        "user_id": "user-456",
        "client_id": "client-789",
        "client_name": "Acme Corp",
        "description": "Monthly retainer",
        "recurrence": "monthly",
        "next_run_date": "2026-04-01",
        "tax_rate": 10.0,
        "auto_send": False,
        "active": True,
        "line_items": [
            {"description": "Monthly Retainer", "quantity": 1, "rate": 5000.00},
        ],
        "created_at": now,
        "updated_at": now,
    }

    # Act
    from models import ScheduleResponse
    schedule = ScheduleResponse(**data)

    # Assert
    assert schedule.id == "sched-123"
    assert schedule.active is True
    assert schedule.recurrence == "monthly"
    assert schedule.client_name == "Acme Corp"


def test_should_create_valid_company_settings_response_model():
    """should create a valid CompanySettingsResponse model with all fields"""
    # Arrange
    now = datetime.utcnow()
    data = {
        "id": "settings-123",
        "user_id": "user-456",
        "company_name": "My Company LLC",
        "company_email": "info@mycompany.com",
        "company_phone": "555-0200",
        "bank_account_name": "My Company LLC",
        "bank_name": "Barclays",
        "account_number": "12345678",
        "sort_code": "20-30-40",
        "iban": "GB29NWBK60161331926819",
        "created_at": now,
        "updated_at": now,
    }

    # Act
    from models import CompanySettingsResponse
    settings = CompanySettingsResponse(**data)

    # Assert
    assert settings.company_name == "My Company LLC"
    assert settings.bank_name == "Barclays"
    assert settings.account_number == "12345678"
    assert settings.sort_code == "20-30-40"


def test_should_create_valid_dashboard_stats_model():
    """should create a valid DashboardStats model"""
    # Arrange
    data = {
        "total_clients": 25,
        "total_invoices": 100,
        "total_revenue": 50000.00,
        "outstanding_amount": 12000.00,
        "overdue_count": 3,
        "paid_this_month": 8000.00,
    }

    # Act
    from models import DashboardStats
    stats = DashboardStats(**data)

    # Assert
    assert stats.total_clients == 25
    assert stats.total_revenue == 50000.00
    assert stats.overdue_count == 3
