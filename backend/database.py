"""
Database operations using async PostgreSQL
"""
import asyncpg
import ssl
from uuid import UUID
from typing import List, Optional, Dict, Any
from config import settings


def _serialize_row(row) -> Dict[str, Any]:
    """Convert a database row to a dict with UUIDs cast to strings"""
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, UUID):
            d[k] = str(v)
    return d


# Global connection pool
pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global pool
    if pool is None:
        # Supabase requires SSL connections; their pooler uses a certificate
        # chain that doesn't pass strict verification, so we encrypt without
        # verifying the cert (equivalent to sslmode=require)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        pool = await asyncpg.create_pool(settings.database_url, ssl=ssl_context)
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
    return [_serialize_row(row) for row in rows]


async def get_client_by_id(client_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get a single client by ID"""
    db = await get_pool()
    row = await db.fetchrow(
        "SELECT * FROM clients WHERE id = $1 AND user_id = $2",
        client_id, user_id
    )
    return _serialize_row(row) if row else None


async def create_client(user_id: str, client) -> Dict[str, Any]:
    """Create a new client"""
    db = await get_pool()
    row = await db.fetchrow(
        """INSERT INTO clients (user_id, name, email, phone, address)
           VALUES ($1, $2, $3, $4, $5)
           RETURNING *""",
        user_id, client.name, client.email, client.phone, client.address
    )
    return _serialize_row(row)


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
    return _serialize_row(row) if row else None


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
        invoice = _serialize_row(row)
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

    invoice = _serialize_row(row)

    # Fetch line items
    line_rows = await db.fetch(
        """SELECT * FROM invoice_line_items
           WHERE invoice_id = $1
           ORDER BY sort_order ASC""",
        invoice_id
    )
    invoice["line_items"] = [_serialize_row(lr) for lr in line_rows]
    return invoice


async def create_invoice(user_id: str, invoice) -> Dict[str, Any]:
    """Create a new invoice with line items"""
    db = await get_pool()

    # Generate next invoice number
    invoice_number = await get_next_invoice_number(user_id)

    # Calculate subtotal from line items
    from decimal import Decimal
    subtotal = sum(Decimal(str(item.quantity)) * Decimal(str(item.rate)) for item in invoice.line_items)
    tax_rate = Decimal(str(invoice.tax_rate))
    tax_amount = subtotal * tax_rate / Decimal("100")
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
    invoice_dict = _serialize_row(row)
    invoice_id = invoice_dict["id"]

    # Insert all line items
    line_items = []
    for idx, item in enumerate(invoice.line_items):
        amount = item.quantity * item.rate
        li_row = await db.fetchrow(
            """INSERT INTO invoice_line_items (
                   invoice_id, description, quantity, rate, amount, sort_order
               ) VALUES ($1, $2, $3, $4, $5, $6)
               RETURNING *""",
            invoice_id, item.description, item.quantity, item.rate, amount, idx
        )
        line_items.append(_serialize_row(li_row))

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
            "DELETE FROM invoice_line_items WHERE invoice_id = $1",
            invoice_id
        )
        for idx, item in enumerate(line_items_data):
            amount = item["quantity"] * item["rate"]
            await db.fetchrow(
                """INSERT INTO invoice_line_items (
                       invoice_id, description, quantity, rate, amount, sort_order
                   ) VALUES ($1, $2, $3, $4, $5, $6)
                   RETURNING *""",
                invoice_id, item["description"], item["quantity"],
                item["rate"], amount, idx
            )

    if needs_recalc:
        # Recalculate from line items in DB
        li_rows = await db.fetch(
            "SELECT quantity, rate FROM invoice_line_items WHERE invoice_id = $1",
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

        from decimal import Decimal
        tax_rate = Decimal(str(tax_rate))
        subtotal = Decimal(str(subtotal))
        tax_amount = subtotal * tax_rate / Decimal("100")
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
        "DELETE FROM invoice_line_items WHERE invoice_id = $1",
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
    return _serialize_row(row) if row else None


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
    return _serialize_row(row)


# ============================================================
# Dashboard operations (placeholder)
# ============================================================

async def get_dashboard_stats(user_id: str) -> Dict[str, Any]:
    """Get dashboard statistics"""
    conn = await get_pool()

    # Total clients
    row = await conn.fetchrow(
        "SELECT COUNT(*) as count FROM clients WHERE user_id = $1", user_id
    )
    total_clients = row["count"] if row else 0

    # Total invoices
    row = await conn.fetchrow(
        "SELECT COUNT(*) as count FROM invoices WHERE user_id = $1", user_id
    )
    total_invoices = row["count"] if row else 0

    # Total revenue (paid invoices)
    row = await conn.fetchrow(
        "SELECT COALESCE(SUM(total_due), 0) as total FROM invoices WHERE user_id = $1 AND status = 'paid'",
        user_id
    )
    total_revenue = float(row["total"]) if row else 0.0

    # Outstanding amount (sent + overdue)
    row = await conn.fetchrow(
        "SELECT COALESCE(SUM(total_due), 0) as total FROM invoices WHERE user_id = $1 AND status IN ('sent', 'overdue')",
        user_id
    )
    outstanding_amount = float(row["total"]) if row else 0.0

    # Overdue count
    row = await conn.fetchrow(
        "SELECT COUNT(*) as count FROM invoices WHERE user_id = $1 AND status = 'overdue'",
        user_id
    )
    overdue_count = row["count"] if row else 0

    # Paid this month
    row = await conn.fetchrow(
        "SELECT COALESCE(SUM(total_due), 0) as total FROM invoices WHERE user_id = $1 AND status = 'paid' AND updated_at >= date_trunc('month', CURRENT_DATE)",
        user_id
    )
    paid_this_month = float(row["total"]) if row else 0.0

    # Draft count
    row = await conn.fetchrow(
        "SELECT COUNT(*) as count FROM invoices WHERE user_id = $1 AND status = 'draft'",
        user_id
    )
    draft_count = row["count"] if row else 0

    # Recent invoices (last 5)
    rows = await conn.fetch(
        """SELECT i.id, i.invoice_number, c.name as client_name, i.total_due, i.status, i.created_at
           FROM invoices i
           LEFT JOIN clients c ON i.client_id = c.id
           WHERE i.user_id = $1
           ORDER BY i.created_at DESC
           LIMIT 5""",
        user_id
    )
    recent_invoices = []
    for r in rows:
        recent_invoices.append({
            "id": str(r["id"]),
            "invoice_number": r["invoice_number"],
            "client_name": r["client_name"],
            "total_due": float(r["total_due"]),
            "status": r["status"],
            "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
        })

    return {
        "total_clients": total_clients,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "outstanding_amount": outstanding_amount,
        "overdue_count": overdue_count,
        "paid_this_month": paid_this_month,
        "draft_count": draft_count,
        "recent_invoices": recent_invoices,
    }


# ============================================================
# Schedule CRUD operations (placeholder)
# ============================================================

async def get_schedules(user_id: str) -> List[Dict[str, Any]]:
    """Get all schedules for a user with client name joined, ordered by next_run_date"""
    db = await get_pool()
    rows = await db.fetch(
        """SELECT s.*, c.name as client_name
           FROM invoice_schedules s
           LEFT JOIN clients c ON s.client_id = c.id
           WHERE s.user_id = $1
           ORDER BY s.next_run_date ASC""",
        user_id
    )
    return [_serialize_row(row) for row in rows]


async def get_schedule_by_id(schedule_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get a single schedule by ID with client name"""
    db = await get_pool()
    row = await db.fetchrow(
        """SELECT s.*, c.name as client_name
           FROM invoice_schedules s
           LEFT JOIN clients c ON s.client_id = c.id
           WHERE s.id = $1 AND s.user_id = $2""",
        schedule_id, user_id
    )
    return _serialize_row(row) if row else None


async def create_schedule(user_id: str, schedule) -> Dict[str, Any]:
    """Create a new recurring invoice schedule"""
    import json
    db = await get_pool()

    # Serialize line items to JSON
    line_items_json = json.dumps([
        {"description": item.description, "quantity": item.quantity, "rate": item.rate}
        for item in schedule.line_items
    ])

    row = await db.fetchrow(
        """INSERT INTO invoice_schedules (
               user_id, client_id, description, line_items, tax_rate,
               recurrence, next_run_date, auto_send
           ) VALUES ($1, $2, $3, $4::jsonb, $5, $6, $7, $8)
           RETURNING *""",
        user_id, schedule.client_id, schedule.description,
        line_items_json, schedule.tax_rate,
        schedule.recurrence.value, schedule.next_run_date, schedule.auto_send
    )
    schedule_dict = _serialize_row(row)

    # Fetch client name
    client_row = await db.fetchrow(
        "SELECT name FROM clients WHERE id = $1",
        schedule.client_id
    )
    schedule_dict["client_name"] = client_row["name"] if client_row else None
    return schedule_dict


async def update_schedule(schedule_id: str, user_id: str, updates) -> Optional[Dict[str, Any]]:
    """Update a schedule with dynamic fields"""
    import json
    update_data = updates.model_dump(exclude_unset=True)
    if not update_data:
        return await get_schedule_by_id(schedule_id, user_id)

    # Handle line_items serialization
    if "line_items" in update_data and update_data["line_items"] is not None:
        update_data["line_items"] = json.dumps([
            {"description": item["description"], "quantity": item["quantity"], "rate": item["rate"]}
            for item in update_data["line_items"]
        ])

    # Convert recurrence enum to string
    if "recurrence" in update_data and update_data["recurrence"] is not None:
        update_data["recurrence"] = (
            update_data["recurrence"].value
            if hasattr(update_data["recurrence"], "value")
            else update_data["recurrence"]
        )

    set_clauses = []
    values = []
    for i, (key, value) in enumerate(update_data.items(), start=1):
        if key == "line_items":
            set_clauses.append(f"{key} = ${i}::jsonb")
        else:
            set_clauses.append(f"{key} = ${i}")
        values.append(value)

    set_clauses.append("updated_at = NOW()")

    param_offset = len(values) + 1
    values.append(schedule_id)
    values.append(user_id)

    query = f"""UPDATE invoice_schedules
                SET {', '.join(set_clauses)}
                WHERE id = ${param_offset} AND user_id = ${param_offset + 1}
                RETURNING *"""

    db = await get_pool()
    row = await db.fetchrow(query, *values)
    if not row:
        return None

    return await get_schedule_by_id(schedule_id, user_id)


async def delete_schedule(schedule_id: str, user_id: str) -> bool:
    """Delete a schedule"""
    db = await get_pool()
    result = await db.execute(
        "DELETE FROM invoice_schedules WHERE id = $1 AND user_id = $2",
        schedule_id, user_id
    )
    return result == "DELETE 1"


async def get_due_schedules() -> List[Dict[str, Any]]:
    """Get all active schedules where next_run_date <= today"""
    db = await get_pool()
    rows = await db.fetch(
        """SELECT s.*, c.name as client_name
           FROM invoice_schedules s
           LEFT JOIN clients c ON s.client_id = c.id
           WHERE s.active = true AND s.next_run_date <= CURRENT_DATE
           ORDER BY s.next_run_date ASC"""
    )
    return [_serialize_row(row) for row in rows]


async def advance_schedule_date(schedule_id: str, recurrence: str) -> None:
    """Calculate and update next_run_date based on recurrence, or deactivate if once"""
    db = await get_pool()

    if recurrence == "once":
        await db.execute(
            """UPDATE invoice_schedules
               SET active = false, updated_at = NOW()
               WHERE id = $1""",
            schedule_id
        )
    else:
        interval_map = {
            "weekly": "7 days",
            "monthly": "1 month",
            "quarterly": "3 months",
            "yearly": "1 year",
        }
        interval = interval_map.get(recurrence, "1 month")
        await db.execute(
            f"""UPDATE invoice_schedules
                SET next_run_date = next_run_date + INTERVAL '{interval}',
                    updated_at = NOW()
                WHERE id = $1""",
            schedule_id
        )
