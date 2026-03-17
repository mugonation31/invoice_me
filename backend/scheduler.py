"""
Scheduler module for processing due invoice schedules
"""
import logging
from datetime import date, timedelta

import database as db
from models import InvoiceCreate, LineItemCreate

logger = logging.getLogger(__name__)


async def process_due_schedules():
    """Find all due schedules and create invoices from them"""
    due_schedules = await db.get_due_schedules()

    for schedule in due_schedules:
        try:
            # Build line items from schedule template
            line_items = [
                LineItemCreate(
                    description=item["description"],
                    quantity=item["quantity"],
                    rate=item["rate"],
                )
                for item in schedule["line_items"]
            ]

            # Calculate due date (30 days from today)
            today = date.today()
            due_date = today + timedelta(days=30)

            # Create invoice from schedule template
            invoice_data = InvoiceCreate(
                client_id=schedule["client_id"],
                issue_date=today,
                due_date=due_date,
                tax_rate=schedule.get("tax_rate", 0),
                line_items=line_items,
            )

            invoice = await db.create_invoice(schedule["user_id"], invoice_data)
            logger.info(
                "Created invoice %s from schedule %s",
                invoice.get("invoice_number", "unknown"),
                schedule["id"],
            )

            # If auto_send, send the invoice
            if schedule.get("auto_send"):
                try:
                    from pdf_generator import generate_invoice_pdf
                    from email_service import send_invoice_email

                    client = await db.get_client_by_id(
                        schedule["client_id"], schedule["user_id"]
                    )
                    company_settings = await db.get_company_settings(schedule["user_id"])
                    if not company_settings:
                        company_settings = {}

                    pdf_bytes = generate_invoice_pdf(invoice, company_settings)
                    await send_invoice_email(
                        to_email=client.get("email", "") if client else "",
                        client_name=client.get("name", "") if client else "",
                        invoice_number=invoice.get("invoice_number", ""),
                        total_due=invoice.get("total_due", 0),
                        pdf_bytes=pdf_bytes,
                        company_name=company_settings.get("company_name"),
                    )
                    await db.update_invoice_status(
                        invoice["id"], schedule["user_id"], "sent"
                    )
                    logger.info("Auto-sent invoice %s", invoice.get("invoice_number"))
                except Exception as e:
                    logger.error("Failed to auto-send invoice: %s", e)

            # Advance the schedule date (or deactivate if once)
            await db.advance_schedule_date(schedule["id"], schedule["recurrence"])

        except Exception as e:
            logger.error("Error processing schedule %s: %s", schedule["id"], e)
