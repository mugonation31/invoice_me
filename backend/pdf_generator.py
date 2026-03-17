"""
Invoice PDF generation using ReportLab
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


def generate_invoice_pdf(invoice: dict, company_settings: dict) -> bytes:
    """Generate PDF bytes for an invoice"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # 1. INVOICE header
    invoice_title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Title"],
        fontSize=28,
        textColor=HexColor("#1a1a2e"),
        spaceAfter=6,
    )
    elements.append(Paragraph("INVOICE", invoice_title_style))

    # 2. Company info
    company_name = company_settings.get("company_name", "")
    company_email = company_settings.get("company_email", "")
    company_phone = company_settings.get("company_phone", "")

    company_style = ParagraphStyle(
        "CompanyInfo",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor("#333333"),
    )
    if company_name:
        bold_company = ParagraphStyle(
            "CompanyName",
            parent=company_style,
            fontSize=12,
            fontName="Helvetica-Bold",
        )
        elements.append(Paragraph(company_name, bold_company))
    if company_email:
        elements.append(Paragraph(company_email, company_style))
    if company_phone:
        elements.append(Paragraph(company_phone, company_style))

    elements.append(Spacer(1, 4 * mm))

    # 3. Invoice metadata
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor("#333333"),
    )
    invoice_number = invoice.get("invoice_number", "")
    issue_date = invoice.get("issue_date", "")
    due_date = invoice.get("due_date", "")

    elements.append(Paragraph(f"Invoice #{invoice_number}", ParagraphStyle(
        "InvoiceNumber", parent=meta_style, fontSize=12, fontName="Helvetica-Bold",
    )))
    elements.append(Paragraph(f"Issue Date: {issue_date}", meta_style))
    elements.append(Paragraph(f"Due Date: {due_date}", meta_style))

    elements.append(Spacer(1, 4 * mm))

    # 4. Horizontal divider (via a thin table)
    divider = Table([[""]],  colWidths=[doc.width])
    divider.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 1, HexColor("#cccccc")),
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 4 * mm))

    # 5. BILL TO section
    bill_to_label = ParagraphStyle(
        "BillToLabel",
        parent=styles["Normal"],
        fontSize=8,
        textColor=HexColor("#888888"),
        fontName="Helvetica",
    )
    elements.append(Paragraph("BILL TO", bill_to_label))

    client_name = invoice.get("client_name", "")
    client_email = invoice.get("client_email", "")
    client_address = invoice.get("client_address", "")

    client_name_style = ParagraphStyle(
        "ClientName", parent=styles["Normal"], fontSize=11, fontName="Helvetica-Bold",
    )
    if client_name:
        elements.append(Paragraph(client_name, client_name_style))
    if client_email:
        elements.append(Paragraph(client_email, meta_style))
    if client_address:
        elements.append(Paragraph(client_address, meta_style))

    elements.append(Spacer(1, 6 * mm))

    # 6. Line items table
    line_items = invoice.get("line_items", [])
    table_data = [["DESCRIPTION", "QUANTITY", "RATE", "AMOUNT"]]
    for item in line_items:
        amount = item.get("amount", item.get("quantity", 0) * item.get("rate", 0))
        table_data.append([
            item.get("description", ""),
            str(item.get("quantity", "")),
            f"\u00a3{item.get('rate', 0):.2f}",
            f"\u00a3{amount:.2f}",
        ])

    col_widths = [doc.width * 0.45, doc.width * 0.15, doc.width * 0.20, doc.width * 0.20]
    line_table = Table(table_data, colWidths=col_widths)

    table_style = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f0f0f0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#555555")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        # Data rows
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        # Alignment
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        # Grid lines
        ("LINEBELOW", (0, 0), (-1, 0), 1, HexColor("#cccccc")),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, HexColor("#eeeeee")),
    ]
    # Add light bottom border for each data row
    for i in range(1, len(table_data)):
        table_style.append(("LINEBELOW", (0, i), (-1, i), 0.5, HexColor("#eeeeee")))

    line_table.setStyle(TableStyle(table_style))
    elements.append(line_table)

    elements.append(Spacer(1, 3 * mm))

    # 7. Horizontal divider
    elements.append(divider)
    elements.append(Spacer(1, 3 * mm))

    # 8. Totals section (right-aligned)
    subtotal = invoice.get("subtotal", 0)
    tax_rate = invoice.get("tax_rate", 0)
    tax_amount = invoice.get("tax_amount", 0)
    total_due = invoice.get("total_due", 0)

    totals_data = [
        ["Subtotal:", f"\u00a3{subtotal:.2f}"],
        [f"Tax ({tax_rate}%):", f"\u00a3{tax_amount:.2f}"],
        ["Total Due:", f"\u00a3{total_due:.2f}"],
    ]
    totals_col_widths = [doc.width * 0.30, doc.width * 0.20]
    totals_table = Table(totals_data, colWidths=totals_col_widths, hAlign="RIGHT")
    totals_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        # Bold total due row
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 12),
        ("LINEABOVE", (0, -1), (-1, -1), 1, HexColor("#333333")),
        ("TOPPADDING", (0, -1), (-1, -1), 8),
    ]))
    elements.append(totals_table)

    elements.append(Spacer(1, 8 * mm))

    # 9. Payment Details block
    bank_account_name = company_settings.get("bank_account_name", "")
    bank_name = company_settings.get("bank_name", "")
    account_number = company_settings.get("account_number", "")
    sort_code = company_settings.get("sort_code", "")
    iban = company_settings.get("iban", "")

    has_payment_details = any([bank_account_name, bank_name, account_number, sort_code, iban])

    if has_payment_details:
        payment_header_style = ParagraphStyle(
            "PaymentHeader",
            parent=styles["Normal"],
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=HexColor("#1a1a2e"),
        )
        payment_label_style = ParagraphStyle(
            "PaymentLabel",
            parent=styles["Normal"],
            fontSize=9,
            textColor=HexColor("#555555"),
        )
        payment_value_style = ParagraphStyle(
            "PaymentValue",
            parent=styles["Normal"],
            fontSize=9,
            fontName="Courier",
            textColor=HexColor("#333333"),
        )

        payment_content = []
        payment_content.append(Paragraph("PAYMENT DETAILS", payment_header_style))
        payment_content.append(Spacer(1, 2 * mm))

        payment_rows = []
        if bank_account_name:
            payment_rows.append(["Bank Account Name:", bank_account_name])
        if bank_name:
            payment_rows.append(["Bank Name:", bank_name])
        if account_number:
            payment_rows.append(["Account Number:", account_number])
        if sort_code:
            payment_rows.append(["Sort Code:", sort_code])
        if iban:
            payment_rows.append(["IBAN:", iban])
        payment_rows.append(["Reference:", invoice_number])

        # Build payment detail paragraphs
        for label, value in payment_rows:
            row_table = Table(
                [[Paragraph(label, payment_label_style), Paragraph(value, payment_value_style)]],
                colWidths=[doc.width * 0.25, doc.width * 0.45],
            )
            row_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]))
            payment_content.append(row_table)

        # Wrap in a table with left border accent
        inner_elements_table = Table(
            [[payment_content]],
            colWidths=[doc.width * 0.75],
        )
        inner_elements_table.setStyle(TableStyle([
            ("LINEBEFORE", (0, 0), (0, -1), 3, HexColor("#1a1a2e")),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(inner_elements_table)

    elements.append(Spacer(1, 10 * mm))

    # 10. Thank you message
    thank_you_style = ParagraphStyle(
        "ThankYou",
        parent=styles["Normal"],
        fontSize=11,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        textColor=HexColor("#333333"),
    )
    elements.append(Paragraph("Thank you for your business!", thank_you_style))

    elements.append(Spacer(1, 2 * mm))

    # 11. Retain copy message
    retain_style = ParagraphStyle(
        "Retain",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=HexColor("#999999"),
    )
    elements.append(Paragraph("Please retain a copy of this invoice for your records.", retain_style))

    doc.build(elements)
    return buffer.getvalue()
