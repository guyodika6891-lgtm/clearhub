import csv
import io
from datetime import datetime
from flask import make_response


def export_requests_csv(requests_list):
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow([
        "Reference", "Student Name", "Student ID", "Semester",
        "Status", "Progress %", "Created", "Completed",
    ])
    for r in requests_list:
        writer.writerow([
            r.reference,
            r.student.full_name or r.student.username,
            r.student.student_id or "",
            r.semester.name,
            r.status,
            r.progress,
            r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
            r.completed_at.strftime("%Y-%m-%d %H:%M") if r.completed_at else "",
        ])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = (
        f"attachment; filename=clearance_requests_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    )
    output.headers["Content-type"] = "text/csv"
    return output


def export_users_csv(users):
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["Username", "Full Name", "Email", "Role", "Student ID",
                     "Department", "Created", "Last Login"])
    for u in users:
        writer.writerow([
            u.username, u.full_name or "", u.email, u.role, u.student_id or "",
            u.department.name if u.department else "",
            u.created_at.strftime("%Y-%m-%d") if u.created_at else "",
            u.last_login_at.strftime("%Y-%m-%d %H:%M") if u.last_login_at else "",
        ])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = (
        f"attachment; filename=users_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    )
    output.headers["Content-type"] = "text/csv"
    return output