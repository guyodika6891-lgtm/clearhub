import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app, request


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


def is_safe_upload(file):
    if not file or not file.filename:
        return False, "No file"
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext in current_app.config.get("BLOCKED_EXTENSIONS", set()):
        return False, f"Extension .{ext} not allowed"
    if not allowed_file(file.filename):
        return False, f"Only {', '.join(current_app.config['ALLOWED_EXTENSIONS'])} allowed"
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > 20 * 1024 * 1024:
        return False, "File too large (max 20 MB)"
    return True, "ok"


def save_upload(file):
    ok, msg = is_safe_upload(file)
    if not ok:
        raise ValueError(msg)
    ext = file.filename.rsplit(".", 1)[-1].lower()
    name = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    file.save(path)
    return name, f"/uploads/{name}"


def audit(action, user_id=None, details=""):
    try:
        from models import AuditLog, db
        log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string[:250] if request else None,
            details=str(details)[:500],
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"[audit] {e}")


def humanize(n):
    n = n or 0
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)


def time_ago(dt):
    if not dt: return ""
    s = int((datetime.utcnow() - dt).total_seconds())
    if s < 60: return "just now"
    if s < 3600: return f"{s//60}m ago"
    if s < 86400: return f"{s//3600}h ago"
    if s < 2592000: return f"{s//86400}d ago"
    if s < 31536000: return f"{s//2592000}mo ago"
    return f"{s//31536000}y ago"