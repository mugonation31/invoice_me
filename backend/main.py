"""
FastAPI backend for Invoice Me app with Supabase authentication
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
from contextlib import asynccontextmanager
from io import BytesIO

# Local imports
from config import settings
from auth import get_current_user
from models import (
    ClientCreate, ClientUpdate, ClientResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, StatusUpdate,
    CompanySettingsUpdate, CompanySettingsResponse,
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    DashboardStats, MessageResponse,
)
import database as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup: Initialize database pool
    await db.get_pool()

    # Start the scheduler
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from scheduler import process_due_schedules
    scheduler = AsyncIOScheduler()
    scheduler.add_job(process_due_schedules, "interval", hours=1, id="process_due_schedules")
    scheduler.start()

    yield

    # Shutdown: Stop scheduler and close database pool
    scheduler.shutdown(wait=False)
    await db.close_pool()


# Create FastAPI app
app = FastAPI(
    title="Invoice Me API",
    description="Backend API for Invoice Me app with Supabase authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoints
@app.get("/")
def root():
    return {"message": "Invoice Me API is running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "OK"}


# ============================================================
# Client endpoints (placeholder)
# ============================================================

@app.get("/api/clients", response_model=List[ClientResponse])
async def get_clients(user_id: str = Depends(get_current_user)):
    """Get all clients for the current user"""
    clients = await db.get_clients(user_id)
    return clients


@app.post("/api/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client: ClientCreate,
    user_id: str = Depends(get_current_user)
):
    """Create a new client"""
    created_client = await db.create_client(user_id, client)
    return created_client


@app.get("/api/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get a specific client by ID"""
    client = await db.get_client_by_id(client_id, user_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client


@app.patch("/api/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    updates: ClientUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update a client"""
    updated_client = await db.update_client(client_id, user_id, updates)
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return updated_client


@app.delete("/api/clients/{client_id}", response_model=MessageResponse)
async def delete_client(
    client_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a client"""
    success = await db.delete_client(client_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return {"message": "Client deleted successfully"}


# ============================================================
# Invoice endpoints (placeholder)
# ============================================================

@app.get("/api/invoices", response_model=List[InvoiceResponse])
async def get_invoices(user_id: str = Depends(get_current_user)):
    """Get all invoices for the current user"""
    invoices = await db.get_invoices(user_id)
    return invoices


@app.post("/api/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice: InvoiceCreate,
    user_id: str = Depends(get_current_user)
):
    """Create a new invoice"""
    created_invoice = await db.create_invoice(user_id, invoice)
    return created_invoice


@app.get("/api/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get a specific invoice by ID"""
    invoice = await db.get_invoice_by_id(invoice_id, user_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice


@app.patch("/api/invoices/{invoice_id}/status", response_model=InvoiceResponse)
async def update_invoice_status(
    invoice_id: str,
    body: StatusUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update invoice status only"""
    updated_invoice = await db.update_invoice_status(invoice_id, user_id, body.status.value)
    if not updated_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return updated_invoice


@app.patch("/api/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    updates: InvoiceUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update an invoice"""
    updated_invoice = await db.update_invoice(invoice_id, user_id, updates)
    if not updated_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return updated_invoice


@app.delete("/api/invoices/{invoice_id}", response_model=MessageResponse)
async def delete_invoice(
    invoice_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete an invoice"""
    success = await db.delete_invoice(invoice_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return {"message": "Invoice deleted successfully"}


@app.post("/api/invoices/{invoice_id}/send")
async def send_invoice(
    invoice_id: str,
    user_id: str = Depends(get_current_user)
):
    """Send invoice via email"""
    from pdf_generator import generate_invoice_pdf
    from email_service import send_invoice_email

    invoice = await db.get_invoice_by_id(invoice_id, user_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    company_settings = await db.get_company_settings(user_id)
    if not company_settings:
        company_settings = {}

    pdf_bytes = generate_invoice_pdf(invoice, company_settings)

    await send_invoice_email(
        to_email=invoice.get("client_email", ""),
        client_name=invoice.get("client_name", ""),
        invoice_number=invoice.get("invoice_number", ""),
        total_due=invoice.get("total_due", 0),
        pdf_bytes=pdf_bytes,
        company_name=company_settings.get("company_name"),
    )

    await db.update_invoice_status(invoice_id, user_id, "sent")

    return {"message": "Invoice sent successfully", "status": "sent"}


@app.get("/api/invoices/{invoice_id}/pdf")
async def get_invoice_pdf(
    invoice_id: str,
    user_id: str = Depends(get_current_user)
):
    """Download invoice as PDF"""
    from pdf_generator import generate_invoice_pdf

    invoice = await db.get_invoice_by_id(invoice_id, user_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    company_settings = await db.get_company_settings(user_id)
    if not company_settings:
        company_settings = {}

    pdf_bytes = generate_invoice_pdf(invoice, company_settings)
    invoice_number = invoice.get("invoice_number", "invoice")

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{invoice_number}.pdf"'
        }
    )


# ============================================================
# Settings endpoints (placeholder)
# ============================================================

@app.get("/api/settings", response_model=CompanySettingsResponse)
async def get_settings(user_id: str = Depends(get_current_user)):
    """Get company settings for the current user"""
    company_settings = await db.get_company_settings(user_id)
    if not company_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found"
        )
    return company_settings


@app.put("/api/settings", response_model=CompanySettingsResponse)
async def update_settings(
    settings_data: CompanySettingsUpdate,
    user_id: str = Depends(get_current_user)
):
    """Create or update company settings"""
    updated_settings = await db.upsert_company_settings(user_id, settings_data)
    return updated_settings


# ============================================================
# Dashboard endpoints (placeholder)
# ============================================================

@app.get("/api/dashboard", response_model=DashboardStats)
async def get_dashboard(user_id: str = Depends(get_current_user)):
    """Get dashboard statistics for the current user"""
    stats = await db.get_dashboard_stats(user_id)
    return stats


# ============================================================
# Schedule endpoints
# ============================================================

@app.get("/api/schedules", response_model=List[ScheduleResponse])
async def get_schedules(user_id: str = Depends(get_current_user)):
    """Get all schedules for the current user"""
    schedules = await db.get_schedules(user_id)
    return schedules


@app.post("/api/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: ScheduleCreate,
    user_id: str = Depends(get_current_user)
):
    """Create a new schedule"""
    created_schedule = await db.create_schedule(user_id, schedule)
    return created_schedule


@app.get("/api/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get a specific schedule by ID"""
    schedule = await db.get_schedule_by_id(schedule_id, user_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return schedule


@app.patch("/api/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    updates: ScheduleUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update a schedule"""
    updated_schedule = await db.update_schedule(schedule_id, user_id, updates)
    if not updated_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return updated_schedule


@app.delete("/api/schedules/{schedule_id}", response_model=MessageResponse)
async def delete_schedule(
    schedule_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a schedule"""
    success = await db.delete_schedule(schedule_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return {"message": "Schedule deleted successfully"}
