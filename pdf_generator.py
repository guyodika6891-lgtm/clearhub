from io import BytesIO
from datetime import datetime
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def generate_clearance_pdf(request_obj, out_path):
    page = A4
    c = canvas.Canvas(out_path, pagesize=page)
    w, h = page

    c.setFillColor(colors.white)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    c.setStrokeColor(colors.HexColor("#1e3a8a"))
    c.setLineWidth(8)
    c.rect(25, 25, w - 50, h - 50)

    c.setStrokeColor(colors.HexColor("#f59e0b"))
    c.setLineWidth(3)
    c.rect(40, 40, w - 80, h - 80)

    c.setStrokeColor(colors.HexColor("#1e3a8a"))
    c.setLineWidth(1)
    c.rect(50, 50, w - 100, h - 100)

    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(w / 2, h - 95, "WERABE UNIVERSITY")

    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(w / 2, h - 115, "Werabe, Ethiopia · Office of the Registrar")

    c.setStrokeColor(colors.HexColor("#f59e0b"))
    c.setLineWidth(2)
    c.line(w / 2 - 200, h - 125, w / 2 + 200, h - 125)

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(w / 2, h - 180, "STUDENT CLEARANCE CERTIFICATE")

    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(w / 2, h - 200, "This document certifies completion of all university clearance requirements")

    box_y = h - 320
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.rect(70, box_y, w - 140, 100, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.setLineWidth(1)
    c.rect(70, box_y, w - 140, 100)

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(90, box_y + 75, "Student Name:")
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.drawString(220, box_y + 74, request_obj.student.full_name or request_obj.student.username)

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(90, box_y + 50, "Student ID:")
    c.setFont("Helvetica", 12)
    c.drawString(220, box_y + 50, request_obj.student.student_id or "—")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(90, box_y + 25, "Semester:")
    c.setFont("Helvetica", 12)
    c.drawString(220, box_y + 25, request_obj.semester.name)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, box_y + 25, "Reference:")
    c.setFont("Helvetica", 11)
    c.drawString(450, box_y + 25, request_obj.reference)

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 15)
    c.drawString(70, h - 355, "Departmental Approvals:")

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.setLineWidth(1)
    c.line(70, h - 365, w - 70, h - 365)

    y = h - 395
    col = 0
    x_left = 80
    x_right = w / 2 + 20

    for step in request_obj.steps:
        if step.status != "approved":
            continue
        x = x_left if col == 0 else x_right

        c.setFillColor(colors.HexColor("#10b981"))
        c.circle(x - 8, y + 2, 8, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x - 8, y - 1, "✓")

        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 6, y, step.department.name[:40])

        c.setFillColor(colors.HexColor("#64748b"))
        c.setFont("Helvetica-Oblique", 7)
        reviewer = (step.reviewer.full_name or step.reviewer.username) if step.reviewer else "Staff"
        date_str = step.reviewed_at.strftime("%b %d, %Y") if step.reviewed_at else ""
        c.drawString(x + 6, y - 10, f"{reviewer}  ·  {date_str}")

        col = 1 - col
        if col == 0:
            y -= 30

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(70, 140, "Date of Issue:")
    c.setFont("Helvetica", 11)
    c.drawString(160, 140, datetime.utcnow().strftime("%B %d, %Y"))

    c.setFont("Helvetica-Bold", 11)
    c.drawString(70, 120, "Verification Code:")
    c.setFont("Courier-Bold", 11)
    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.drawString(180, 120, request_obj.reference)

    c.setStrokeColor(colors.HexColor("#0f172a"))
    c.setLineWidth(1)
    c.line(w - 240, 150, w - 90, 150)
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawCentredString(w - 165, 137, "Registrar")
    c.drawCentredString(w - 165, 125, "Signature & Stamp")

    qr = qrcode.make(
        f"Werabe University Clearance\n"
        f"Ref: {request_obj.reference}\n"
        f"Student: {request_obj.student.username}"
    )
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    c.drawImage(ImageReader(buf), w - 130, 55, width=75, height=75)

    c.setFillColor(colors.HexColor("#94a3b8"))
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(w / 2, 45,
        "This certificate is valid only with the Registrar's signature and official university stamp.")
    c.drawCentredString(w / 2, 32,
        f"Generated automatically on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

    c.showPage()
    c.save()
    return out_path