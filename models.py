import secrets
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import func
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student", index=True)

    full_name = db.Column(db.String(120), default="")
    student_id = db.Column(db.String(40), default="", index=True)
    phone = db.Column(db.String(30), default="")
    college = db.Column(db.String(120), default="")
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)

    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship("Department", foreign_keys=[department_id])
    requests = db.relationship("ClearanceRequest", backref="student",
                               lazy="dynamic", foreign_keys="ClearanceRequest.student_id")
    steps_reviewed = db.relationship("ClearanceStep", backref="reviewer",
                                     lazy="dynamic", foreign_keys="ClearanceStep.reviewed_by")
    notifications = db.relationship("Notification", backref="user",
                                    lazy="dynamic", cascade="all, delete-orphan")

    @property
    def is_admin(self): return self.role == "admin"
    @property
    def is_staff(self): return self.role == "staff"
    @property
    def is_student(self): return self.role == "student"

    @property
    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.utcnow()

    @property
    def unread_count(self):
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    contact_email = db.Column(db.String(120), default="")
    contact_phone = db.Column(db.String(30), default="")
    location = db.Column(db.String(120), default="")
    order_index = db.Column(db.Integer, default=0, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_optional = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    steps = db.relationship("ClearanceStep", backref="department", lazy="dynamic")

    @property
    def pending_count(self):
        return self.steps.filter_by(status="pending").count()

    @property
    def approved_count(self):
        return self.steps.filter_by(status="approved").count()

    @property
    def rejected_count(self):
        return self.steps.filter_by(status="rejected").count()


class Semester(db.Model):
    __tablename__ = "semesters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requests = db.relationship("ClearanceRequest", backref="semester", lazy="dynamic")


class ClearanceRequest(db.Model):
    __tablename__ = "clearance_requests"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(40), unique=True, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    semester_id = db.Column(db.Integer, db.ForeignKey("semesters.id"), nullable=False)
    status = db.Column(db.String(20), default="pending", index=True)
    reason = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    steps = db.relationship("ClearanceStep", backref="request",
                            lazy="dynamic", cascade="all, delete-orphan",
                            order_by="ClearanceStep.id")
    documents = db.relationship("Document", backref="request",
                                lazy="dynamic", cascade="all, delete-orphan")
    messages = db.relationship("RequestMessage", backref="request",
                               lazy="dynamic", cascade="all, delete-orphan")

    @property
    def progress(self):
        total = self.steps.filter(ClearanceStep.department.has(is_optional=False)).count()
        if total == 0: return 0
        approved = self.steps.filter_by(status="approved")\
            .filter(ClearanceStep.department.has(is_optional=False)).count()
        return int((approved / total) * 100)

    @property
    def is_complete(self):
        total = self.steps.filter(ClearanceStep.department.has(is_optional=False)).count()
        if total == 0: return False
        approved = self.steps.filter_by(status="approved")\
            .filter(ClearanceStep.department.has(is_optional=False)).count()
        return approved == total

    @property
    def current_step(self):
        return self.steps.filter_by(status="pending")\
            .join(Department, Department.id == ClearanceStep.department_id)\
            .order_by(Department.order_index).first()

    @property
    def total_steps(self):
        return self.steps.count()

    @property
    def approved_steps(self):
        return self.steps.filter_by(status="approved").count()


class ClearanceStep(db.Model):
    __tablename__ = "clearance_steps"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("clearance_requests.id"),
                           nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"),
                              nullable=False, index=True)
    status = db.Column(db.String(20), default="pending", index=True)
    comment = db.Column(db.Text, default="")
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('request_id', 'department_id',
                            name='uq_request_department'),
    )


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("clearance_requests.id"),
                           nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    original_name = db.Column(db.String(255), default="")
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    message = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(300), default="")
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


# ============ PAYMENTS ============
class FeePayment(db.Model):
    __tablename__ = "fee_payments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default="usd")
    description = db.Column(db.String(200), default="Clearance fee")
    status = db.Column(db.String(20), default="pending")
    stripe_session_id = db.Column(db.String(200), unique=True, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("User", foreign_keys=[student_id])
    department = db.relationship("Department")


# ============ CHAT ============
class RequestMessage(db.Model):
    __tablename__ = "request_messages"
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("clearance_requests.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    author = db.relationship("User")


def generate_reference():
    return f"CLR-{secrets.token_hex(4).upper()}"