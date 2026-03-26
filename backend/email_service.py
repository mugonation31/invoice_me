"""
Email sending service using Resend
"""
import base64
import html as html_mod
import resend
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
    """Send invoice PDF via Resend email"""
    resend.api_key = settings.resend_api_key
    sender = from_email or settings.resend_from_email
    company = company_name or "Our Company"

    safe_client = html_mod.escape(client_name)
    safe_invoice = html_mod.escape(invoice_number)
    safe_company = html_mod.escape(company)

    resend.Emails.send({
        "from": f"{safe_company} <{sender}>",
        "to": [to_email],
        "subject": f"Invoice {safe_invoice} from {safe_company}",
        "html": f"""
        <p>Dear {safe_client},</p>
        <p>Please find attached invoice {safe_invoice} for &pound;{total_due:.2f}.</p>
        <p>Thank you for your business.</p>
        <p>{safe_company}</p>
        """,
        "attachments": [
            {
                "filename": f"Invoice-{invoice_number}.pdf",
                "content": list(pdf_bytes),
            }
        ],
    })

    return True
