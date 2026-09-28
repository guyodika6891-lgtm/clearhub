import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_PROD = os.environ.get("FLASK_ENV") == "production"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    APP_URL = os.environ.get("APP_URL", "http://127.0.0.1:5000")

    # ============ DATABASE ============
    database_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'clearance.db')}"
    )
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }

    # ============ UPLOADS ============
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(BASE_DIR, "static", "uploads")
    )
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
    BLOCKED_EXTENSIONS = {
        "php", "py", "rb", "pl", "sh", "exe", "bat", "cmd",
        "jsp", "asp", "aspx", "cgi", "htm", "html", "svg", "js",
    }

    # ============ SECURITY ============
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_PROD
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = IS_PROD
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    RATE_LOGIN = "5 per minute"
    RATE_REGISTER = "3 per hour"
    RATE_DEFAULT = "500 per day;120 per hour"
    RATE_STEP_REVIEW = "60 per hour"
    RATE_DOCUMENT_UPLOAD = "10 per hour"

    # ============ MAIL ============
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "")

    # ============ UNIVERSITY INFO ============
    UNIVERSITY_NAME = "Werabe University"
    UNIVERSITY_ADDRESS = "Werabe, Ethiopia"
    UNIVERSITY_REGISTRAR = "Office of the Registrar"

    # ============ ALL UNIVERSITY DEPARTMENTS ============
    DEFAULT_DEPARTMENTS = [
        {"name": "Department (Academic)", "code": "DEP", "order_index": 1,
         "description": "Academic department head approval"},
        {"name": "Laboratory", "code": "LAB", "order_index": 2,
         "description": "Lab equipment return & dues"},
        {"name": "Library", "code": "LIB", "order_index": 3,
         "description": "Return all library books and settle fines"},
        {"name": "ICT / Computer Center", "code": "ICT", "order_index": 4,
         "description": "Return any lab/IT equipment"},
        {"name": "Dormitory", "code": "DOR", "order_index": 5,
         "description": "Return dorm keys and furniture"},
        {"name": "Cafeteria", "code": "CAF", "order_index": 6,
         "description": "Clear cafeteria bills and meal cards"},
        {"name": "Student Services", "code": "STU", "order_index": 7,
         "description": "Student ID, student union dues"},
        {"name": "University Hospital / Health Center", "code": "HOS", "order_index": 8,
         "description": "Medical dues and clearance"},
        {"name": "Sports & Recreation", "code": "SPR", "order_index": 9,
         "description": "Return sports equipment"},
        {"name": "Student Union", "code": "UNI", "order_index": 10,
         "description": "Student union dues and ID return"},
        {"name": "Finance / Cashier", "code": "FIN", "order_index": 11,
         "description": "Settle all university fees"},
        {"name": "Security Office", "code": "SEC", "order_index": 12,
         "description": "Return access cards, ID, all property"},
        {"name": "Registrar", "code": "REG", "order_index": 13,
         "description": "Final approval — documents, transcripts"},
        {"name": "Postgraduate Office", "code": "PGD", "order_index": 14,
         "description": "For postgraduate students only", "is_optional": True},
        {"name": "Research & Grants", "code": "RES", "order_index": 15,
         "description": "Research project clearance", "is_optional": True},
        {"name": "Alumni Office", "code": "ALM", "order_index": 16,
         "description": "Alumni registration"},
    ]

    # ============ APP CONSTANTS ============
    ROLES = ["admin", "staff", "student"]
    REQUEST_STATUS = ["pending", "in_progress", "approved", "rejected", "completed"]
    STEP_STATUS = ["pending", "approved", "rejected", "skipped"]

    ROLE_LABELS = {
        "admin": "Administrator",
        "staff": "Department Staff",
        "student": "Student",
    }