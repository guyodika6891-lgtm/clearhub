from datetime import datetime, timedelta
from models import ClearanceRequest, ClearanceStep, User
from notifications import notify


def check_stalled_requests(days=3):
    cutoff = datetime.utcnow() - timedelta(days=days)
    stalled = (
        ClearanceStep.query
        .filter_by(status="pending")
        .join(ClearanceRequest)
        .filter(ClearanceRequest.created_at < cutoff)
        .all()
    )
    alerts = 0
    for step in stalled:
        staff_users = User.query.filter_by(
            department_id=step.department_id, role="staff"
        ).all()
        for s in staff_users:
            notify(
                s.id,
                f"⏰ Overdue: {step.request.student.full_name or step.request.student.username}'s "
                f"clearance has been waiting on {step.department.name} for "
                f"{(datetime.utcnow() - step.request.created_at).days} days.",
                f"/step/{step.id}/review"
            )
            alerts += 1
    return alerts


def notify_students_of_stalled(days=7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    stalled = ClearanceRequest.query.filter(
        ClearanceRequest.status.in_(["pending", "in_progress"]),
        ClearanceRequest.created_at < cutoff,
    ).all()
    for req in stalled:
        current = req.current_step
        if not current:
            continue
        notify(
            req.student_id,
            f"⏰ Your clearance has been waiting on {current.department.name} for "
            f"{(datetime.utcnow() - req.created_at).days} days.",
            f"/clearance/{req.reference}"
        )
    return len(stalled)