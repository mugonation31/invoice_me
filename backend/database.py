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
# Invoice CRUD operations
# ============================================================

async def get_next_invoice_number(user_id: str) -> str:
    """Generate next invoice number for a user (INV-0001 format)"""
    db = await get_pool()
    row = await db.fetchrow(
        "SELECT COUNT(*) as count FROM invoices WHERE user_id = $1",
        user_id
    )
    next_num = (row["count"] if row else 0) + 1
    return f"INV-{next_num:04d}"


async def get_invoices(user_id: str) -> List[Dict[str, Any]]:
    """Get all invoices for a user with client name joined, ordered by created_at DESC.
    Does NOT fetch line items (list view doesn't need them)."""
    db = await get_pool()
    rows = await db.fetch(
        """SELECT i.*, c.name as client_name, c.email as client_email
           FROM invoices i
           LEFT JOIN clients c ON i.client_id = c.id
           WHERE i.user_id = $1
           ORDER BY i.created_at DESC""",
        user_id
    )
    result = []
    for row in rows:
        invoice = dict(row)
        invoice["line_items"] = []
        result.append(invoice)
    return result


async def get_invoice_by_id(invoice_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get a single invoice by ID with client name AND all its line items."""
    db = await get_pool()
    # Fetch invoice with client info
    row = await db.fetchrow(
        """SELECT i.*, c.name as client_name, c.email as client_email
           FROM invoices i
           LEFT JOIN clients c ON i.client_id = c.id
           WHERE i.id = $1 AND i.user_id = $2""",
        invoice_id, user_id
    )
    if not row:
        return None

    invoice = dict(row)

    # Fetch line items
    line_rows = await db.fetch(
        """SELECT * FROM line_items
           WHERE invoice_id = $1
           ORDER BY sort_order ASC""",
        invoice_id
    )
    invoice["line_items"] = [dict(lr) for lr in line_rows]
    return invoice


async def create_invoice(user_id: str, invoice) -> Dict[str, Any]:
    """Create a new invoice with line items"""
    db = await get_pool()

    # Generate next invoice number
    invoice_number = await get_next_invoice_number(user_id)

    # Calculate subtotal from line items
    subtotal = sum(item.quantity * item.rate for item in invoice.line_items)
    tax_amount = subtotal * invoice.tax_rate / 100
    total_due = subtotal + tax_amount

    # Insert invoice record
    row = await db.fetchrow(
        """INSERT INTO invoices (
               user_id, client_id, invoice_number, status,
               issue_date, due_date, tax_rate, subtotal, tax_amount, total_due, notes
           ) VALUES ($1, $2, $3, 'draft', $4, $5, $6, $7, $8, $9, $10)
           RETURNING *""",
        user_id, invoice.client_id, invoice_number,
        invoice.issue_date, invoice.due_date, invoice.tax_rate,
        subtotal, tax_amount, total_due, invoice.notes
    )
    invoice_dict = dict(row)
    invoice_id = invoice_dict["id"]

    # Insert all line items
    line_items = []
    for idx, item in enumerate(invoice.line_items):
        amount = item.quantity * item.rate
        li_row = await db.fetchrow(
            """INSERT INTO line_items (
                   invoice_id, description, quantity, rate, amount, sort_order
               ) VALUES ($1, $2, $3, $4, $5, $6)
               RETURNING *""",
            invoice_id, item.description, item.quantity, item.rate, amount, idx
        )
        line_items.append(dict(li_row))

    invoice_dict["line_items"] = line_items

    # Fetch client name/email
    client_row = await db.fetchrow(
        "SELECT name, email FROM clients WHERE id = $1",
        invoice.client_id
    )
    invoice_dict["client_name"] = client_row["name"] if client_row else None
    invoice_dict["client_email"] = client_row["email"] if client_row else None

    return invoice_dict


async def update_invoice(invoice_id: str, user_id: str, updates) -> Optional[Dict[str, Any]]:
    """Update an invoice with dynamic fields"""
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        return await get_invoice_by_id(invoice_id, user_id)

    db = await get_pool()

    # Handle line items separately
    line_items_data = update_data.pop("line_items", None)

    # If line_items or tax_rate changed, recalculate totals
    needs_recalc = line_items_data is not None or "tax_rate" in update_data

    if line_items_data is not None:
        # Delete existing line items and re-insert
        await db.execute(
            "DELETE FROM line_items WHERE invoice_id = $1",
            invoice_id
        )
        for idx, item in enumerate(line_items_data):
            amount = item["quantity"] * item["rate"]
            await db.fetchrow(
                """INSERT INTO line_items (
                       invoice_id, description, quantity, rate, amount, sort_order
                   ) VALUES ($1, $2, $3, $4, $5, $6)
                   RETURNING *""",
                invoice_id, item["description"], item["quantity"],
                item["rate"], amount, idx
            )

    if needs_recalc:
        # Recalculate from line items in DB
        li_rows = await db.fetch(
            "SELECT quantity, rate FROM line_items WHERE invoice_id = $1",
            invoice_id
        )
        subtotal = sum(r["quantity"] * r["rate"] for r in li_rows)

        # Get tax_rate: use updated value if provided, otherwise fetch current
        if "tax_rate" in update_data:
            tax_rate = update_data["tax_rate"]
        else:
            current = await db.fetchrow(
                "SELECT tax_rate FROM invoices WHERE id = $1",
                invoice_id
            )
            tax_rate = current["tax_rate"] if current else 0

        tax_amount = subtotal * tax_rate / 100
        total_due = subtotal + tax_amount

        update_data["subtotal"] = subtotal
        update_data["tax_amount"] = tax_amount
        update_data["total_due"] = total_due

    # Convert status enum to string if present
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = update_data["status"].value if hasattr(update_data["status"], "value") else update_data["status"]

    # Build SET clause from remaining fields
    if update_data:
        set_clauses = []
        values = []
        for i, (key, value) in enumerate(update_data.items(), start=1):
            set_clauses.append(f"{key} = ${i}")
            values.append(value)

        set_clauses.append("updated_at = NOW()")

        param_offset = len(values) + 1
        values.append(invoice_id)
        values.append(user_id)

        query = f"""UPDATE invoices
                    SET {', '.join(set_clauses)}
                    WHERE id = ${param_offset} AND user_id = ${param_offset + 1}
                    RETURNING *"""

        row = await db.fetchrow(query, *values)
        if not row:
            return None
    else:
        # Only line items changed, just touch updated_at
        row = await db.fetchrow(
            """UPDATE invoices SET updated_at = NOW()
               WHERE id = $1 AND user_id = $2
               RETURNING *""",
            invoice_id, user_id
        )
        if not row:
            return None

    return await get_invoice_by_id(invoice_id, user_id)


async def delete_invoice(invoice_id: str, user_id: str) -> bool:
    """Delete an invoice (cascade deletes line items)"""
    db = await get_pool()
    # Delete line items first
    await db.execute(
        "DELETE FROM line_items WHERE invoice_id = $1",
        invoice_id
    )
    result = await db.execute(
        "DELETE FROM invoices WHERE id = $1 AND user_id = $2",
        invoice_id, user_id
    )
    return result == "DELETE 1"


async def update_invoice_status(invoice_id: str, user_id: str, status: str) -> Optional[Dict[str, Any]]:
    """Update invoice status only"""
    db = await get_pool()
    row = await db.fetchrow(
        """UPDATE invoices
           SET status = $1, updated_at = NOW()
           WHERE id = $2 AND user_id = $3
           RETURNING *""",
        status, invoice_id, user_id
    )
    if not row:
        return None
    return await get_invoice_by_id(invoice_id, user_id)


# ============================================================
# Company Settings CRUD operations (placeholder)
# ============================================================

async def get_company_settings(user_id: str) -> Optional[Dict[str, Any]]:
    """Get company settings for a user"""
    db = await get_pool()
    row = await db.fetchrow(
        "SELECT * FROM company_settings WHERE user_id = $1",
        user_id
    )
    return dict(row) if row else None


async def upsert_company_settings(user_id: str, settings_data) -> Dict[str, Any]:
    """Create or update company settings (upsert)"""
    update_data = settings_data.model_dump(exclude_unset=True)

    db = await get_pool()
    row = await db.fetchrow(
        """INSERT INTO company_settings (
               user_id, company_name, company_email, company_phone,
               bank_account_name, bank_name, account_number, sort_code, iban
           ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
           ON CONFLICT (user_id) DO UPDATE SET
               company_name = COALESCE($2, company_settings.company_name),
               company_email = COALESCE($3, company_settings.company_email),
               company_phone = COALESCE($4, company_settings.company_phone),
               bank_account_name = COALESCE($5, company_settings.bank_account_name),
               bank_name = COALESCE($6, company_settings.bank_name),
               account_number = COALESCE($7, company_settings.account_number),
               sort_code = COALESCE($8, company_settings.sort_code),
               iban = COALESCE($9, company_settings.iban),
               updated_at = NOW()
           RETURNING *""",
        user_id,
        update_data.get("company_name"),
        update_data.get("company_email"),
        update_data.get("company_phone"),
        update_data.get("bank_account_name"),
        update_data.get("bank_name"),
        update_data.get("account_number"),
        update_data.get("sort_code"),
        update_data.get("iban"),
    )
    return dict(row)


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
