"""
FastAPI backend for Invoice Me app with Supabase authentication
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from contextlib import asynccontextmanager

# Local imports
from config import settings
from auth import get_current_user
from models import (
    ClientCreate, ClientUpdate, ClientResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, StatusUpdate,
    CompanySettingsUpdate, CompanySettingsResponse,
    DashboardStats, MessageResponse,
)
import database as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup: Initialize database pool
    await db.get_pool()
    yield
    # Shutdown: Close database pool
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
