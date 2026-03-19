"""
Email sending service using SendGrid
"""
import base64
import html as html_mod
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition
)
from config import settings


async def send_invoice_email(
    to_email: str,
    client_name: str,
    invoice_number: str,
    total_due: float,
    pdf_bytes: bytes,
    from_email: str = None,
    company_name: str = None
) -> bool:
    """Send invoice PDF via SendGrid email"""
    sender = from_email or settings.sendgrid_from_email
    company = company_name or "Our Company"

    safe_client = html_mod.escape(client_name)
    safe_invoice = html_mod.escape(invoice_number)
    safe_company = html_mod.escape(company)

    message = Mail(
        from_email=sender,
        to_emails=to_email,
        subject=f"Invoice {safe_invoice} from {safe_company}",
        html_content=f"""
        <p>Dear {safe_client},</p>
        <p>Please find attached invoice {safe_invoice} for &pound;{total_due:.2f}.</p>
        <p>Thank you for your business.</p>
        <p>{safe_company}</p>
        """,
    )

    encoded_pdf = base64.b64encode(pdf_bytes).decode()
    attachment = Attachment(
        FileContent(encoded_pdf),
        FileName(f"Invoice-{invoice_number}.pdf"),
        FileType("application/pdf"),
        Disposition("attachment"),
    )
    message.attachment = attachment

    sg = SendGridAPIClient(settings.sendgrid_api_key)
    sg.send(message)
    return True
