from flask import current_app, render_template_string
from flask_mail import Message
from mailer import mail


TEMPLATES = {
    "step_approved": """
        <h2 style="color:#10b981;">✅ {{ department }} approved your clearance</h2>
        <p>Hi {{ name }},</p>
        <p>Your clearance ({{ reference }}) has been approved by <strong>{{ department }}</strong>.</p>
        <p>Current progress: <strong>{{ progress }}%</strong></p>
        {% if next_dept %}
          <p>Next department: <strong>{{ next_dept }}</strong></p>
        {% endif %}
        <p><a href="{{ url }}" style="background:#2563eb;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">View Request</a></p>
    """,
    "step_rejected": """
        <h2 style="color:#ef4444;">❌ {{ department }} rejected your clearance</h2>
        <p>Hi {{ name }},</p>
        <p>Your clearance ({{ reference }}) was <strong>rejected</strong> by {{ department }}.</p>
        <p><strong>Reason:</strong> {{ reason }}</p>
        <p><a href="{{ url }}" style="background:#2563eb;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">View Request</a></p>
    """,
    "completed": """
        <h2 style="color:#10b981;">🎉 Your clearance is complete!</h2>
        <p>Hi {{ name }},</p>
        <p>Congratulations! Your clearance ({{ reference }}) is fully approved.</p>
        <p><a href="{{ url }}" style="background:#2563eb;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">Download Certificate</a></p>
    """,
}


def _send(to_email, subject, html):
    if not current_app.config.get("MAIL_USERNAME"):
        return
    try:
        msg = Message(subject, recipients=[to_email])
        msg.html = html
        mail.send(msg)
    except Exception as e:
        print(f"[email error] {e}")


def notify_approved(request_obj, step, next_step=None):
    html = render_template_string(
        TEMPLATES["step_approved"],
        name=request_obj.student.full_name or request_obj.student.username,
        reference=request_obj.reference,
        department=step.department.name,
        progress=request_obj.progress,
        next_dept=next_step.department.name if next_step else None,
        url=f"{current_app.config.get('APP_URL','')}/clearance/{request_obj.reference}",
    )
    _send(request_obj.student.email,
          f"✅ {step.department.name} approved your clearance", html)


def notify_rejected(request_obj, step):
    html = render_template_string(
        TEMPLATES["step_rejected"],
        name=request_obj.student.full_name or request_obj.student.username,
        reference=request_obj.reference,
        department=step.department.name,
        reason=step.comment or "(no reason provided)",
        url=f"{current_app.config.get('APP_URL','')}/clearance/{request_obj.reference}",
    )
    _send(request_obj.student.email,
          f"❌ {step.department.name} rejected your clearance", html)


def notify_completed(request_obj):
    html = render_template_string(
        TEMPLATES["completed"],
        name=request_obj.student.full_name or request_obj.student.username,
        reference=request_obj.reference,
        url=f"{current_app.config.get('APP_URL','')}/clearance/{request_obj.reference}/certificate",
    )
    _send(request_obj.student.email, "🎉 Your clearance is complete", html)