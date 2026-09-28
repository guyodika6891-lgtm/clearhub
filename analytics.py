from datetime import datetime, timedelta, date
from sqlalchemy import func
from extensions import db
from models import ClearanceRequest, ClearanceStep, Department, User


def get_analytics_overview():
    total = ClearanceRequest.query.count()
    completed = ClearanceRequest.query.filter_by(status="completed").count()
    rejected = ClearanceRequest.query.filter_by(status="rejected").count()
    in_progress = ClearanceRequest.query.filter_by(status="in_progress").count()
    completion_rate = round((completed / total * 100), 1) if total else 0

    completed_requests = ClearanceRequest.query.filter_by(status="completed").all()
    times = []
    for r in completed_requests:
        if r.completed_at and r.created_at:
            times.append((r.completed_at - r.created_at).total_seconds() / 86400)
    avg_completion_days = round(sum(times) / len(times), 1) if times else 0

    days, counts = [], []
    for i in range(29, -1, -1):
        day = date.today() - timedelta(days=i)
        days.append(day.strftime("%b %d"))
        counts.append(
            ClearanceRequest.query.filter(
                func.date(ClearanceRequest.created_at) == day
            ).count()
        )

    status_counts = {
        s: ClearanceRequest.query.filter_by(status=s).count()
        for s in ["pending", "in_progress", "approved", "rejected", "completed"]
    }

    return {
        "total": total, "completed": completed, "in_progress": in_progress,
        "rejected": rejected, "completion_rate": completion_rate,
        "avg_completion_days": avg_completion_days,
        "days": days, "counts": counts, "status_counts": status_counts,
    }


def department_bottlenecks():
    depts = Department.query.filter_by(is_active=True).all()
    result = []
    for d in depts:
        pending = ClearanceStep.query.filter_by(
            department_id=d.id, status="pending"
        ).all()
        pending_days = [(datetime.utcnow() - s.request.created_at).days for s in pending]
        avg_pending = round(sum(pending_days) / len(pending_days), 1) if pending_days else 0

        approved = ClearanceStep.query.filter_by(
            department_id=d.id, status="approved"
        ).all()
        approval_times = [
            (s.reviewed_at - s.request.created_at).total_seconds() / 86400
            for s in approved if s.reviewed_at
        ]
        avg_approval = round(sum(approval_times) / len(approval_times), 1) if approval_times else 0

        result.append({
            "dept": d, "pending": len(pending),
            "avg_pending_days": avg_pending,
            "approved": len(approved),
            "avg_approval_days": avg_approval,
        })
    result.sort(key=lambda x: x["avg_pending_days"], reverse=True)
    return result


def stale_requests(days=7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    return ClearanceRequest.query.filter(
        ClearanceRequest.status.in_(["pending", "in_progress"]),
        ClearanceRequest.created_at < cutoff,
    ).order_by(ClearanceRequest.created_at).all()