import os
import secrets
from datetime import datetime, timedelta, date
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, abort, send_from_directory, jsonify, send_file
)
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, desc, func

from config import Config, IS_PROD
from extensions import db, login_manager, csrf
from models import (
    User, Department, Semester, ClearanceRequest, ClearanceStep,
    Document, Notification, AuditLog, FeePayment, RequestMessage,
    generate_reference
)
from forms import (
    RegisterForm, LoginForm, ClearanceRequestForm, StepReviewForm,
    DocumentForm, DepartmentForm, SemesterForm, ProfileForm
)
from decorators import admin_required, staff_required, student_required
from utils import save_upload, audit, humanize, time_ago
from pdf_generator import generate_clearance_pdf
from mailer import init_mail, send_verification_email, verify_token
from email_notifications import notify_approved, notify_rejected, notify_completed
import notifications as notif

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[Config.RATE_DEFAULT],
    storage_uri="memory://",
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    init_mail(app)
    socketio.init_app(app)
    notif.init(socketio)

    csp = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'",
                       "https://cdn.jsdelivr.net",
                       "https://cdn.socket.io",
                       "https://cdnjs.cloudflare.com"],
        'style-src': ["'self'", "'unsafe-inline'",
                      "https://cdn.jsdelivr.net",
                      "https://cdnjs.cloudflare.com",
                      "https://fonts.googleapis.com"],
        'font-src': ["'self'", "https://fonts.gstatic.com",
                     "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
        'img-src': ["'self'", "data:", "https:"],
        'connect-src': ["'self'", "wss:", "https:"],
        'frame-src': ["'self'"],
        'object-src': ["'none'"],
        'base-uri': ["'self'"],
    }
    Talisman(
        app,
        content_security_policy=csp,
        force_https=IS_PROD,
        session_cookie_secure=IS_PROD,
        frame_options="SAMEORIGIN",
        referrer_policy="strict-origin-when-cross-origin",
        strict_transport_security=IS_PROD,
    )

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    with app.app_context():
        db.create_all()
        seed_defaults()

    app.jinja_env.filters["humanize"] = humanize
    app.jinja_env.filters["time_ago"] = time_ago

    register_routes(app)
    register_socket_events()
    register_errors(app)
    return app


def seed_defaults():
    if Department.query.count() == 0:
        for d in Config.DEFAULT_DEPARTMENTS:
            db.session.add(Department(**d))
        db.session.commit()

    if Semester.query.count() == 0:
        year = datetime.utcnow().year
        db.session.add(Semester(
            name=f"Academic Year {year}",
            start_date=date(year, 9, 1),
            end_date=date(year + 1, 6, 30),
            is_active=True,
        ))
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def register_errors(app):
    @app.errorhandler(403)
    def forbidden(e): return render_template("403.html"), 403

    @app.errorhandler(404)
    def nf(e): return render_template("404.html"), 404

    @app.errorhandler(429)
    def ratelimit(e): return render_template("429.html", error=str(e)), 429

    @app.errorhandler(500)
    def se(e):
        db.session.rollback()
        try: audit("SERVER_ERROR", details=str(e)[:400])
        except: pass
        return render_template("500.html"), 500


def register_socket_events():
    @socketio.on("connect")
    def on_connect():
        if current_user.is_authenticated:
            join_room(f"user_{current_user.id}")

    @socketio.on("join_department")
    def join_department(data):
        if current_user.is_authenticated and current_user.is_staff:
            join_room(f"dept_{current_user.department_id}")


def register_routes(app):

    # ============ HOME ============
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        dept_count = Department.query.filter_by(is_active=True).count()
        return render_template("index.html", dept_count=dept_count)

    # ============ PUBLIC QR VERIFICATION ============
    @app.route("/verify/<ref>")
    def public_verify(ref):
        req = ClearanceRequest.query.filter_by(reference=ref).first()
        return render_template("public_verify.html", req=req)

    @app.route("/qr/<ref>.png")
    def qr_png(ref):
        from qr_verify import generate_qr_png, verification_url
        req = ClearanceRequest.query.filter_by(reference=ref).first_or_404()
        buf = generate_qr_png(verification_url(req, external=True))
        return send_file(buf, mimetype="image/png")

    # ============ AI ASSISTANT ============
    @app.route("/ai/ask", methods=["POST"])
    @login_required
    @limiter.limit("20 per hour")
    def ai_ask():
        from ai_assistant import ask_ai
        data = request.get_json() or {}
        question = str(data.get("question", "")).strip()[:500]
        if not question:
            return jsonify({"error": "No question"}), 400
        answer = ask_ai(question, current_user)
        return jsonify({"answer": answer})

    # ============ AUTH ============
    @app.route("/register", methods=["GET", "POST"])
    @limiter.limit(Config.RATE_REGISTER)
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        form = RegisterForm()
        if form.validate_on_submit():
            username = form.username.data.strip()
            email = form.email.data.strip().lower()
            if User.query.filter((User.username == username) | (User.email == email)).first():
                flash("Username or email already taken.", "danger")
            else:
                role = form.role.data
                if User.query.count() == 0:
                    role = "admin"
                user = User(
                    username=username, email=email,
                    full_name=form.full_name.data.strip(),
                    student_id=form.student_id.data or "",
                    phone=form.phone.data or "",
                    role=role,
                    password=generate_password_hash(form.password.data),
                )
                db.session.add(user)
                db.session.commit()
                audit("REGISTER", user.id, f"role={role}")
                try: send_verification_email(user)
                except: pass
                login_user(user)
                flash("Welcome!", "success")
                return redirect(url_for("dashboard"))
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit(Config.RATE_LOGIN)
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data.strip()
            user = User.query.filter_by(username=username).first()

            if user and user.is_locked:
                remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60) + 1
                audit("LOGIN_LOCKED", user.id, f"user={username}")
                flash(f"Account locked. Try again in {remaining} min.", "danger")
                return render_template("login.html", form=form)

            if user and check_password_hash(user.password, form.password.data):
                user.failed_login_attempts = 0
                user.locked_until = None
                user.last_login_at = datetime.utcnow()
                user.last_login_ip = request.remote_addr
                db.session.commit()
                login_user(user, remember=True)
                audit("LOGIN_SUCCESS", user.id)
                flash(f"Welcome back, {user.username}!", "success")
                return redirect(request.args.get("next") or url_for("dashboard"))

            if user:
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                if user.failed_login_attempts >= Config.MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=Config.LOCKOUT_DURATION_MINUTES)
                    audit("LOGIN_LOCKOUT", user.id, f"after {user.failed_login_attempts} attempts")
                    flash(f"Too many attempts. Locked for {Config.LOCKOUT_DURATION_MINUTES} min.", "danger")
                else:
                    audit("LOGIN_FAILED", user.id)
                    flash("Invalid credentials.", "danger")
                db.session.commit()
            else:
                audit("LOGIN_FAILED", details=f"unknown user={username}")
                flash("Invalid credentials.", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        audit("LOGOUT", current_user.id)
        logout_user()
        flash("Logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/verify-email/<token>")
    def verify_email(token):
        email = verify_token(token)
        if not email:
            flash("Invalid link.", "danger")
            return redirect(url_for("login"))
        user = User.query.filter_by(email=email).first()
        if user:
            user.email_verified = True
            db.session.commit()
            audit("EMAIL_VERIFIED", user.id)
            flash("✅ Email verified!", "success")
        return redirect(url_for("login"))

    # ============ DASHBOARD ============
    @app.route("/dashboard")
    @login_required
    def dashboard():
        if current_user.is_admin: return redirect(url_for("admin_dashboard"))
        if current_user.is_staff: return redirect(url_for("staff_dashboard"))
        return redirect(url_for("student_dashboard"))

    @app.route("/dashboard/student")
    @login_required
    @student_required
    def student_dashboard():
        requests = current_user.requests.order_by(desc(ClearanceRequest.created_at)).all()
        active = next((r for r in requests if r.status in ("pending", "in_progress")), None)
        completed = [r for r in requests if r.status == "completed"]
        return render_template("dashboard_student.html",
                               requests=requests, active=active, completed=completed)

    @app.route("/clearance/apply", methods=["GET", "POST"])
    @login_required
    @student_required
    def clearance_apply():
        existing = current_user.requests.filter(
            ClearanceRequest.status.in_(["pending", "in_progress"])
        ).first()
        if existing:
            flash("You already have an active clearance request.", "warning")
            return redirect(url_for("clearance_detail", ref=existing.reference))

        form = ClearanceRequestForm()
        form.semester_id.choices = [(s.id, s.name) for s in
                                    Semester.query.filter_by(is_active=True).all()]
        if form.validate_on_submit():
            semester = Semester.query.get(form.semester_id.data)
            if not semester:
                flash("Invalid semester.", "danger")
                return redirect(url_for("clearance_apply"))

            req = ClearanceRequest(
                reference=generate_reference(),
                student_id=current_user.id,
                semester_id=semester.id,
                reason=form.reason.data or "",
                status="in_progress",
            )
            db.session.add(req)
            db.session.flush()

            departments = Department.query.filter_by(is_active=True).order_by(Department.order_index).all()
            for d in departments:
                if d.is_optional:
                    continue
                db.session.add(ClearanceStep(
                    request_id=req.id, department_id=d.id, status="pending",
                ))
            db.session.commit()
            audit("CLEARANCE_APPLIED", current_user.id, f"ref={req.reference}")

            first_step = req.current_step
            if first_step:
                staff_users = User.query.filter_by(
                    department_id=first_step.department_id, role="staff"
                ).all()
                for s in staff_users:
                    notif.notify(s.id,
                                 f"New clearance from {current_user.full_name or current_user.username}",
                                 url_for("staff_step_review", step_id=first_step.id))

            flash(f"Clearance submitted! Ref: {req.reference}", "success")
            return redirect(url_for("clearance_detail", ref=req.reference))
        return render_template("clearance_apply.html", form=form)

    @app.route("/clearance/<ref>")
    @login_required
    def clearance_detail(ref):
        req = ClearanceRequest.query.filter_by(reference=ref).first_or_404()
        if not current_user.is_admin and req.student_id != current_user.id:
            if not (current_user.is_staff and current_user.department_id and
                    req.steps.filter_by(department_id=current_user.department_id).first()):
                abort(403)
        steps = req.steps.join(Department).order_by(Department.order_index).all()
        return render_template("clearance_detail.html", req=req, steps=steps,
                               document_form=DocumentForm())

    @app.route("/clearance/<ref>/document", methods=["POST"])
    @login_required
    @student_required
    @limiter.limit(Config.RATE_DOCUMENT_UPLOAD)
    def clearance_upload_document(ref):
        req = ClearanceRequest.query.filter_by(reference=ref).first_or_404()
        if req.student_id != current_user.id:
            abort(403)
        form = DocumentForm()
        if form.validate_on_submit() and form.file.data:
            try:
                filename, url = save_upload(form.file.data)
                doc = Document(
                    request_id=req.id, filename=filename, url=url,
                    original_name=form.file.data.filename,
                )
                db.session.add(doc)
                db.session.commit()
                audit("DOCUMENT_UPLOADED", current_user.id, f"ref={ref}")
                flash("Document uploaded.", "success")
            except ValueError as e:
                flash(str(e), "danger")
        else:
            flash("Please select a valid file.", "danger")
        return redirect(url_for("clearance_detail", ref=ref))

    @app.route("/dashboard/staff")
    @login_required
    @staff_required
    def staff_dashboard():
        if not current_user.department_id and not current_user.is_admin:
            flash("You are not assigned to a department. Contact admin.", "warning")
            return redirect(url_for("profile"))
        dept = current_user.department
        pending_steps = []
        recent_reviews = []
        if dept:
            pending_steps = ClearanceStep.query.filter_by(
                department_id=dept.id, status="pending"
            ).order_by(ClearanceStep.id).all()
            recent_reviews = ClearanceStep.query.filter_by(
                department_id=dept.id, reviewed_by=current_user.id
            ).order_by(desc(ClearanceStep.reviewed_at)).limit(10).all()
        return render_template("dashboard_staff.html", dept=dept,
                               pending_steps=pending_steps, recent_reviews=recent_reviews)

    @app.route("/step/<int:step_id>/review", methods=["GET", "POST"])
    @login_required
    @staff_required
    def staff_step_review(step_id):
        step = ClearanceStep.query.get_or_404(step_id)
        if not current_user.is_admin and step.department_id != current_user.department_id:
            abort(403)

        req = step.request
        current = req.current_step
        if current and current.id != step.id and not current_user.is_admin:
            flash("It's not your department's turn yet.", "warning")
            return redirect(url_for("staff_dashboard"))

        form = StepReviewForm()
        if form.validate_on_submit():
            step.status = form.status.data
            step.comment = form.comment.data or ""
            step.reviewed_by = current_user.id
            step.reviewed_at = datetime.utcnow()

            if step.status == "approved":
                msg = f"✅ {step.department.name} approved your clearance"
            else:
                msg = f"❌ {step.department.name} rejected: {step.comment[:100]}"
            notif.notify(req.student_id, msg, url_for("clearance_detail", ref=req.reference))
            db.session.commit()

            # Email notifications
            try:
                if step.status == "approved":
                    notify_approved(req, step, req.current_step)
                else:
                    notify_rejected(req, step)
            except Exception as e:
                print(f"[email notify] {e}")

            if req.is_complete:
                req.status = "completed"
                req.completed_at = datetime.utcnow()
                db.session.commit()
                notif.notify(req.student_id,
                             "🎉 Your clearance is COMPLETE! Download your certificate.",
                             url_for("clearance_certificate", ref=req.reference))
                try: notify_completed(req)
                except Exception as e: print(f"[email notify] {e}")
                audit("CLEARANCE_COMPLETED", current_user.id, f"ref={req.reference}")
            else:
                next_step = req.current_step
                if next_step and step.status == "approved":
                    staff_users = User.query.filter_by(
                        department_id=next_step.department_id, role="staff"
                    ).all()
                    for s in staff_users:
                        notif.notify(s.id,
                                     f"New clearance from {req.student.full_name or req.student.username}",
                                     url_for("staff_step_review", step_id=next_step.id))

            audit("STEP_REVIEW", current_user.id, f"step={step.id} status={step.status}")
            flash(f"Decision recorded: {step.status}", "success")
            return redirect(url_for("staff_dashboard"))

        return render_template("staff_step_review.html", step=step, form=form, req=req)

    # ============ ADMIN ============
    @app.route("/dashboard/admin")
    @login_required
    @admin_required
    def admin_dashboard():
        stats = {
            "users": User.query.count(),
            "students": User.query.filter_by(role="student").count(),
            "staff": User.query.filter_by(role="staff").count(),
            "departments": Department.query.filter_by(is_active=True).count(),
            "requests_total": ClearanceRequest.query.count(),
            "requests_pending": ClearanceRequest.query.filter(
                ClearanceRequest.status.in_(["pending", "in_progress"])
            ).count(),
            "requests_completed": ClearanceRequest.query.filter_by(status="completed").count(),
        }
        dept_load = []
        for d in Department.query.filter_by(is_active=True).order_by(Department.order_index).all():
            dept_load.append({
                "dept": d, "pending": d.pending_count,
                "approved": d.approved_count, "rejected": d.rejected_count,
            })
        recent_requests = ClearanceRequest.query.order_by(
            desc(ClearanceRequest.created_at)).limit(10).all()
        recent_audit = AuditLog.query.order_by(desc(AuditLog.created_at)).limit(15).all()
        return render_template("dashboard_admin.html",
                               stats=stats, dept_load=dept_load,
                               recent_requests=recent_requests, recent_audit=recent_audit)

    @app.route("/admin/analytics")
    @login_required
    @admin_required
    def admin_analytics():
        days, counts = [], []
        for i in range(29, -1, -1):
            day = datetime.utcnow().date() - timedelta(days=i)
            days.append(day.strftime("%b %d"))
            counts.append(ClearanceRequest.query.filter(
                func.date(ClearanceRequest.created_at) == day
            ).count())
        status_counts = {
            s: ClearanceRequest.query.filter_by(status=s).count()
            for s in Config.REQUEST_STATUS
        }
        dept_times = []
        for d in Department.query.filter_by(is_active=True).all():
            approved = ClearanceStep.query.filter_by(
                department_id=d.id, status="approved"
            ).all()
            if approved:
                times = []
                for s in approved:
                    if s.reviewed_at and s.request.created_at:
                        times.append((s.reviewed_at - s.request.created_at).total_seconds() / 3600)
                avg = sum(times) / len(times) if times else 0
                dept_times.append({"dept": d, "avg_hours": round(avg, 1)})
        return render_template("admin_analytics.html",
                               days=days, counts=counts,
                               status_counts=status_counts, dept_times=dept_times)

    # ============ REPORTS ============
    @app.route("/admin/reports")
    @login_required
    @admin_required
    def admin_reports():
        return render_template("admin_reports.html")

    @app.route("/admin/reports/requests.csv")
    @login_required
    @admin_required
    def admin_export_requests():
        from reports import export_requests_csv
        requests_list = ClearanceRequest.query.order_by(
            desc(ClearanceRequest.created_at)).all()
        return export_requests_csv(requests_list)

    @app.route("/admin/reports/users.csv")
    @login_required
    @admin_required
    def admin_export_users():
        from reports import export_users_csv
        return export_users_csv(User.query.all())

    @app.route("/admin/heatmap")
    @login_required
    @admin_required
    def admin_heatmap():
        from analytics import department_bottlenecks
        return render_template("admin_heatmap.html", bottlenecks=department_bottlenecks())

    @app.route("/admin/stalled")
    @login_required
    @admin_required
    def admin_stalled():
        from analytics import stale_requests
        return render_template("admin_requests.html",
                               requests=stale_requests(7),
                               status="", q="")

    # ============ ADMIN: USERS ============
    @app.route("/admin/users")
    @login_required
    @admin_required
    def admin_users():
        q = request.args.get("q", "").strip()[:100]
        role = request.args.get("role", "").strip()
        query = User.query
        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                User.username.ilike(like),
                User.email.ilike(like),
                User.full_name.ilike(like),
                User.student_id.ilike(like),
            ))
        if role:
            query = query.filter_by(role=role)
        users = query.order_by(desc(User.created_at)).limit(100).all()
        return render_template("admin_users.html", users=users, q=q, role=role,
                               departments=Department.query.order_by(Department.order_index).all())

    @app.route("/admin/user/<int:user_id>/role", methods=["POST"])
    @login_required
    @admin_required
    def admin_set_role(user_id):
        u = User.query.get_or_404(user_id)
        new_role = request.form.get("role")
        if new_role in Config.ROLES:
            u.role = new_role
            db.session.commit()
            audit("ADMIN_SET_ROLE", current_user.id, f"user={u.username} role={new_role}")
            flash(f"Role updated to {new_role}", "success")
        return redirect(request.referrer or url_for("admin_users"))

    @app.route("/admin/user/<int:user_id>/department", methods=["POST"])
    @login_required
    @admin_required
    def admin_set_department(user_id):
        u = User.query.get_or_404(user_id)
        dept_id = request.form.get("department_id", type=int)
        u.department_id = dept_id if dept_id else None
        db.session.commit()
        audit("ADMIN_SET_DEPT", current_user.id, f"user={u.username} dept={dept_id}")
        flash("Department assigned.", "success")
        return redirect(request.referrer or url_for("admin_users"))

    @app.route("/admin/user/<int:user_id>/unlock", methods=["POST"])
    @login_required
    @admin_required
    def admin_unlock_user(user_id):
        u = User.query.get_or_404(user_id)
        u.locked_until = None
        u.failed_login_attempts = 0
        db.session.commit()
        audit("ADMIN_UNLOCK", current_user.id, f"user={u.username}")
        flash(f"{u.username} unlocked.", "success")
        return redirect(request.referrer or url_for("admin_users"))

    # ============ ADMIN: DEPARTMENTS ============
    @app.route("/admin/departments")
    @login_required
    @admin_required
    def admin_departments():
        depts = Department.query.order_by(Department.order_index).all()
        return render_template("admin_departments.html", departments=depts)

    @app.route("/admin/department/new", methods=["GET", "POST"])
    @login_required
    @admin_required
    def admin_department_new():
        form = DepartmentForm()
        if form.validate_on_submit():
            if Department.query.filter_by(code=form.code.data.upper()).first():
                flash("Code already exists.", "danger")
            else:
                d = Department(
                    name=form.name.data.strip(),
                    code=form.code.data.strip().upper(),
                    description=form.description.data or "",
                    contact_email=form.contact_email.data or "",
                    order_index=int(form.order_index.data),
                    is_active=form.is_active.data,
                )
                db.session.add(d)
                db.session.commit()
                audit("DEPT_CREATE", current_user.id, f"code={d.code}")
                flash("Department created.", "success")
                return redirect(url_for("admin_departments"))
        return render_template("admin_department_form.html", form=form, dept=None)

    @app.route("/admin/department/<int:dept_id>/edit", methods=["GET", "POST"])
    @login_required
    @admin_required
    def admin_department_edit(dept_id):
        d = Department.query.get_or_404(dept_id)
        form = DepartmentForm(obj=d)
        if form.validate_on_submit():
            d.name = form.name.data.strip()
            d.code = form.code.data.strip().upper()
            d.description = form.description.data or ""
            d.contact_email = form.contact_email.data or ""
            d.order_index = int(form.order_index.data)
            d.is_active = form.is_active.data
            db.session.commit()
            audit("DEPT_EDIT", current_user.id, f"code={d.code}")
            flash("Department updated.", "success")
            return redirect(url_for("admin_departments"))
        return render_template("admin_department_form.html", form=form, dept=d)

    @app.route("/admin/department/<int:dept_id>/toggle", methods=["POST"])
    @login_required
    @admin_required
    def admin_department_toggle(dept_id):
        d = Department.query.get_or_404(dept_id)
        d.is_active = not d.is_active
        db.session.commit()
        audit("DEPT_TOGGLE", current_user.id, f"code={d.code} active={d.is_active}")
        flash(f"Department {'activated' if d.is_active else 'deactivated'}.", "success")
        return redirect(url_for("admin_departments"))

    # ============ ADMIN: SEMESTERS ============
    @app.route("/admin/semesters")
    @login_required
    @admin_required
    def admin_semesters():
        semesters = Semester.query.order_by(desc(Semester.created_at)).all()
        return render_template("admin_semesters.html", semesters=semesters)

    @app.route("/admin/semester/new", methods=["GET", "POST"])
    @login_required
    @admin_required
    def admin_semester_new():
        form = SemesterForm()
        if form.validate_on_submit():
            s = Semester(
                name=form.name.data.strip(),
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                is_active=form.is_active.data,
            )
            db.session.add(s)
            db.session.commit()
            audit("SEM_CREATE", current_user.id, f"name={s.name}")
            flash("Semester created.", "success")
            return redirect(url_for("admin_semesters"))
        return render_template("admin_semester_form.html", form=form)

    # ============ ADMIN: ALL REQUESTS ============
    @app.route("/admin/requests")
    @login_required
    @admin_required
    def admin_requests():
        status = request.args.get("status", "").strip()
        q = request.args.get("q", "").strip()[:100]
        query = ClearanceRequest.query
        if status:
            query = query.filter_by(status=status)
        if q:
            like = f"%{q}%"
            query = query.join(User, User.id == ClearanceRequest.student_id)\
                .filter(or_(
                    User.username.ilike(like),
                    User.full_name.ilike(like),
                    User.student_id.ilike(like),
                    ClearanceRequest.reference.ilike(like),
                ))
        requests_list = query.order_by(desc(ClearanceRequest.created_at)).limit(200).all()
        return render_template("admin_requests.html",
                               requests=requests_list, status=status, q=q)

    # ============ CHAT ============
    @app.route("/clearance/<ref>/chat", methods=["GET", "POST"])
    @login_required
    def request_chat(ref):
        req = ClearanceRequest.query.filter_by(reference=ref).first_or_404()
        if not current_user.is_admin and req.student_id != current_user.id:
            if not (current_user.is_staff and current_user.department_id and
                    req.steps.filter_by(department_id=current_user.department_id).first()):
                abort(403)

        if request.method == "POST":
            body = request.form.get("body", "").strip()[:2000]
            if body:
                msg = RequestMessage(
                    request_id=req.id, user_id=current_user.id, body=body,
                )
                db.session.add(msg)
                db.session.commit()
                if current_user.id != req.student_id:
                    notif.notify(req.student_id,
                                 f"💬 New message from {current_user.full_name or current_user.username}",
                                 url_for("request_chat", ref=ref))
                return redirect(url_for("request_chat", ref=ref))

        messages = RequestMessage.query.filter_by(request_id=req.id)\
            .order_by(RequestMessage.created_at).all()
        return render_template("request_chat.html", req=req, messages=messages)

    # ============ CERTIFICATE ============
    @app.route("/clearance/<ref>/certificate")
    @login_required
    def clearance_certificate(ref):
        req = ClearanceRequest.query.filter_by(reference=ref).first_or_404()
        if req.student_id != current_user.id and not current_user.is_admin:
            abort(403)
        if not req.is_complete:
            flash("Clearance not complete yet.", "warning")
            return redirect(url_for("clearance_detail", ref=ref))
        return render_template("certificate.html", req=req)

    @app.route("/clearance/<ref>/certificate.pdf")
    @login_required
    def clearance_certificate_pdf(ref):
        req = ClearanceRequest.query.filter_by(reference=ref).first_or_404()
        if req.student_id != current_user.id and not current_user.is_admin:
            abort(403)
        if not req.is_complete:
            abort(403)
        tmp_dir = os.path.join(app.config["UPLOAD_FOLDER"], "certificates")
        os.makedirs(tmp_dir, exist_ok=True)
        path = os.path.join(tmp_dir, f"{req.reference}.pdf")
        generate_clearance_pdf(req, path)
        return send_file(path, as_attachment=True,
                         download_name=f"clearance-{req.reference}.pdf")

    # ============ NOTIFICATIONS ============
    @app.route("/notifications")
    @login_required
    def notifications_view():
        notifs = Notification.query.filter_by(user_id=current_user.id)\
            .order_by(desc(Notification.created_at)).limit(50).all()
        notif.mark_read(current_user.id)
        return render_template("notifications.html", notifications=notifs)

    @app.route("/notifications/count")
    @login_required
    def notifications_count():
        return jsonify({"count": current_user.unread_count})

    # ============ LANGUAGE ============
    @app.route("/lang/<code>")
    def set_language(code):
        from multi_lang import set_lang
        set_lang(code)
        return redirect(request.referrer or url_for("dashboard"))

    # ============ PROFILE ============
    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        form = ProfileForm(obj=current_user)
        if form.validate_on_submit():
            current_user.full_name = form.full_name.data or ""
            current_user.phone = form.phone.data or ""
            current_user.student_id = form.student_id.data or ""
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))
        return render_template("profile.html", form=form)

    # ============ FILES ============
    @app.route("/uploads/<path:filename>")
    @login_required
    def uploaded_file(filename):
        filename = os.path.basename(filename)
        response = send_from_directory(app.config["UPLOAD_FOLDER"], filename)
        response.headers["Content-Disposition"] = "inline"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.route("/healthz")
    def healthz():
        return {"status": "ok", "time": datetime.utcnow().isoformat()}


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=not IS_PROD,
                 allow_unsafe_werkzeug=True)