"""
Database operations using async PostgreSQL
"""
import asyncpg
from typing import List, Optional, Dict, Any
from config import settings


# Global connection pool
pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(settings.database_url)
    return pool


async def close_pool():
    """Close database connection pool"""
    global pool
    if pool:
        await pool.close()
        pool = None


# ============================================================
# Client CRUD operations
# ============================================================

async def get_clients(user_id: str) -> List[Dict[str, Any]]:
    """Get all clients for a user, ordered by name"""
    db = await get_pool()
    rows = await db.fetch(
        "SELECT * FROM clients WHERE user_id = $1 ORDER BY name ASC",
        user_id
    )
    return [dict(row) for row in rows]


async def get_client_by_id(client_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get a single client by ID"""
    db = await get_pool()
    row = await db.fetchrow(
        "SELECT * FROM clients WHERE id = $1 AND user_id = $2",
        client_id, user_id
    )
    return dict(row) if row else None


async def create_client(user_id: str, client) -> Dict[str, Any]:
    """Create a new client"""
    db = await get_pool()
    row = await db.fetchrow(
        """INSERT INTO clients (user_id, name, email, phone, address)
           VALUES ($1, $2, $3, $4, $5)
           RETURNING *""",
        user_id, client.name, client.email, client.phone, client.address
    )
    return dict(row)


async def update_client(client_id: str, user_id: str, updates) -> Optional[Dict[str, Any]]:
    """Update a client with dynamic fields"""
    # Build SET clause from non-None fields
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        return await get_client_by_id(client_id, user_id)

    set_clauses = []
    values = []
    for i, (key, value) in enumerate(update_data.items(), start=1):
        set_clauses.append(f"{key} = ${i}")
        values.append(value)

    # Add updated_at
    set_clauses.append(f"updated_at = NOW()")

    # Add client_id and user_id as the last parameters
    param_offset = len(values) + 1
    values.append(client_id)
    values.append(user_id)

    query = f"""UPDATE clients
                SET {', '.join(set_clauses)}
                WHERE id = ${param_offset} AND user_id = ${param_offset + 1}
                RETURNING *"""

    db = await get_pool()
    row = await db.fetchrow(query, *values)
    return dict(row) if row else None


async def delete_client(client_id: str, user_id: str) -> bool:
    """Delete a client (hard delete)"""
    db = await get_pool()
    result = await db.execute(
        "DELETE FROM clients WHERE id = $1 AND user_id = $2",
        client_id, user_id
    )
    return result == "DELETE 1"


# ============================================================
# Invoice CRUD operations (placeholder)
# ============================================================

async def get_invoices(user_id: str) -> List[Dict[str, Any]]:
    """Get all invoices for a user"""
    pass


async def get_invoice_by_id(invoice_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get a single invoice by ID"""
    pass


async def create_invoice(user_id: str, invoice) -> Dict[str, Any]:
    """Create a new invoice with line items"""
    pass


async def update_invoice(invoice_id: str, user_id: str, updates) -> Optional[Dict[str, Any]]:
    """Update an invoice"""
    pass


async def delete_invoice(invoice_id: str, user_id: str) -> bool:
    """Delete an invoice"""
    pass


# ============================================================
# Company Settings CRUD operations (placeholder)
# ============================================================

async def get_company_settings(user_id: str) -> Optional[Dict[str, Any]]:
    """Get company settings for a user"""
    pass


async def upsert_company_settings(user_id: str, settings_data) -> Dict[str, Any]:
    """Create or update company settings"""
    pass


# ============================================================
# Dashboard operations (placeholder)
# ============================================================

async def get_dashboard_stats(user_id: str) -> Dict[str, Any]:
    """Get dashboard statistics"""
    pass


# ============================================================
# Schedule CRUD operations (placeholder)
# ============================================================

async def get_schedules(user_id: str) -> List[Dict[str, Any]]:
    """Get all recurring invoice schedules for a user"""
    pass


async def create_schedule(user_id: str, schedule) -> Dict[str, Any]:
    """Create a new recurring invoice schedule"""
    pass


async def update_schedule(schedule_id: str, user_id: str, updates) -> Optional[Dict[str, Any]]:
    """Update a schedule"""
    pass


async def delete_schedule(schedule_id: str, user_id: str) -> bool:
    """Delete a schedule"""
    pass
