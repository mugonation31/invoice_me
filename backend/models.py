"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice status levels"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"


class ClientCreate(BaseModel):
    """Schema for creating a new client"""
    name: str = Field(..., min_length=1, max_length=200, description="Client name")
    email: str = Field(..., description="Client email")
    phone: Optional[str] = Field(None, max_length=50, description="Client phone")
    address: Optional[str] = Field(None, max_length=500, description="Client address")


class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)


class ClientResponse(BaseModel):
    """Schema for client response"""
    id: str
    user_id: str
    name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LineItemCreate(BaseModel):
    """Schema for creating an invoice line item"""
    description: str = Field(..., min_length=1, max_length=500, description="Line item description")
    quantity: float = Field(..., gt=0, description="Quantity")
    unit_price: float = Field(..., ge=0, description="Unit price")


class LineItemResponse(BaseModel):
    """Schema for line item response"""
    id: str
    invoice_id: str
    description: str
    quantity: float
    unit_price: float
    line_total: float

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    """Schema for creating a new invoice"""
    client_id: str = Field(..., description="Client ID")
    due_date: Optional[datetime] = Field(None, description="Due date")
    line_items: List[LineItemCreate] = Field(default_factory=list, description="Invoice line items")
    notes: Optional[str] = Field(None, max_length=2000, description="Invoice notes")


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice"""
    client_id: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)
    line_items: Optional[List[LineItemCreate]] = None


class InvoiceResponse(BaseModel):
    """Schema for invoice response"""
    id: str
    user_id: str
    client_id: str
    invoice_number: str
    status: InvoiceStatus
    due_date: Optional[datetime]
    subtotal: float
    tax_rate: Optional[float]
    tax_amount: Optional[float]
    total: float
    notes: Optional[str]
    line_items: List[LineItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleCreate(BaseModel):
    """Schema for creating a recurring invoice schedule"""
    client_id: str = Field(..., description="Client ID")
    frequency: str = Field(..., description="Frequency: weekly, monthly, quarterly, yearly")
    next_run: datetime = Field(..., description="Next scheduled run date")
    line_items: List[LineItemCreate] = Field(default_factory=list, description="Line items template")


class ScheduleResponse(BaseModel):
    """Schema for schedule response"""
    id: str
    user_id: str
    client_id: str
    frequency: str
    next_run: datetime
    is_active: bool
    line_items: List[LineItemCreate] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanySettingsUpdate(BaseModel):
    """Schema for updating company settings"""
    company_name: Optional[str] = Field(None, max_length=200)
    company_email: Optional[str] = None
    company_phone: Optional[str] = Field(None, max_length=50)
    bank_account_name: Optional[str] = Field(None, max_length=200)
    bank_name: Optional[str] = Field(None, max_length=200)
    account_number: Optional[str] = Field(None, max_length=50)
    sort_code: Optional[str] = Field(None, max_length=20)
    iban: Optional[str] = Field(None, max_length=50)


class CompanySettingsResponse(BaseModel):
    """Schema for company settings response"""
    id: str
    user_id: str
    company_name: Optional[str]
    company_email: Optional[str]
    company_phone: Optional[str]
    bank_account_name: Optional[str]
    bank_name: Optional[str]
    account_number: Optional[str]
    sort_code: Optional[str]
    iban: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total_clients: int
    total_invoices: int
    total_revenue: float
    outstanding_amount: float
    overdue_count: int
    paid_this_month: float


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
