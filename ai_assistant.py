import os
from datetime import datetime
from openai import OpenAI
from models import ClearanceRequest, ClearanceStep

_client = None


def _client_get():
    global _client
    if _client is None and os.environ.get("OPENAI_API_KEY"):
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


SYSTEM_PROMPT = """You are ClearHub AI, a friendly university clearance assistant.

You help students understand their clearance status and what to do next.
You help staff identify bottlenecks and prioritize work.

Be concise (2-4 sentences max).
Use plain language. Be encouraging.
Never invent data — only use what's in the context provided.
"""


def _build_user_context(user):
    if user.is_student:
        requests = user.requests.order_by(ClearanceRequest.created_at.desc()).all()
        if not requests:
            return "The student has not submitted any clearance request yet."

        lines = [f"Student: {user.full_name or user.username}"]
        for req in requests[:3]:
            lines.append(f"\nRequest {req.reference} ({req.semester.name}):")
            lines.append(f"  Status: {req.status} ({req.progress}% complete)")
            lines.append(f"  Created: {req.created_at.strftime('%b %d, %Y')}")
            for step in req.steps.order_by(ClearanceStep.id):
                reviewer = (step.reviewer.full_name or step.reviewer.username) if step.reviewer else None
                line = f"  - {step.department.name}: {step.status}"
                if step.reviewed_at:
                    line += f" (reviewed {step.reviewed_at.strftime('%b %d')} by {reviewer})"
                if step.comment:
                    line += f" — comment: {step.comment[:100]}"
                lines.append(line)
            current = req.current_step
            if current:
                days = (datetime.utcnow() - req.created_at).days
                lines.append(f"  Currently waiting on: {current.department.name}")
                lines.append(f"  Total wait: {days} days")
        return "\n".join(lines)

    elif user.is_staff:
        dept = user.department
        if not dept:
            return "Staff member is not assigned to a department."
        pending = ClearanceStep.query.filter_by(
            department_id=dept.id, status="pending"
        ).all()
        lines = [f"Staff: {user.full_name or user.username}"]
        lines.append(f"Department: {dept.name} ({dept.code})")
        lines.append(f"Pending reviews: {len(pending)}")
        for s in pending[:10]:
            days = (datetime.utcnow() - s.request.created_at).days
            lines.append(f"  - {s.request.student.full_name or s.request.student.username} "
                         f"({s.request.reference}) — waiting {days} days")
        return "\n".join(lines)

    elif user.is_admin:
        total = ClearanceRequest.query.count()
        pending = ClearanceRequest.query.filter(
            ClearanceRequest.status.in_(["pending", "in_progress"])
        ).count()
        completed = ClearanceRequest.query.filter_by(status="completed").count()
        return (f"Admin: {user.username}\nTotal: {total}\n"
                f"Pending: {pending}\nCompleted: {completed}")

    return "No context available."


def ask_ai(question, user, history=None):
    client = _client_get()
    if client is None:
        return "⚠️ AI is not configured yet. Ask your admin to add an OPENAI_API_KEY."

    context = _build_user_context(user)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Current user context:\n{context}"},
    ]
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": question})

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.5,
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI unavailable: {e}"