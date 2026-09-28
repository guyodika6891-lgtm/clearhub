from flask import session

TRANSLATIONS = {
    "en": {
        "welcome": "Welcome", "dashboard": "Dashboard", "login": "Login",
        "register": "Register", "logout": "Logout",
        "apply_clearance": "Apply for Clearance", "my_requests": "My Requests",
        "pending_reviews": "Pending Reviews", "admin_panel": "Admin Panel",
        "departments": "Departments", "analytics": "Analytics",
        "notifications": "Notifications", "profile": "Profile",
        "students": "Students", "staff": "Staff",
        "approve": "Approve", "reject": "Reject",
        "submit": "Submit", "cancel": "Cancel",
    },
    "am": {
        "welcome": "እንኳን ደህና መጡ", "dashboard": "ዳሽቦርድ", "login": "ግባ",
        "register": "ተመዝገብ", "logout": "ውጣ",
        "apply_clearance": "ክሊራንስ ያመልክቱ", "my_requests": "የእኔ ጥያቄዎች",
        "pending_reviews": "በመጠባበቅ ላይ", "admin_panel": "የአስተዳዳሪ ፓናል",
        "departments": "መምሪያዎች", "analytics": "ትንታኔ",
        "notifications": "ማሳወቂያዎች", "profile": "መገለጫ",
        "students": "ተማሪዎች", "staff": "ሰራተኞች",
        "approve": "ፍቀድ", "reject": "አትፍቀድ", "submit": "አስገባ", "cancel": "ሰርዝ",
    },
    "om": {
        "welcome": "Baga nagaan dhufte", "dashboard": "Daashboordii",
        "login": "Seeni", "register": "Galmaa'i", "logout": "Ba'i",
        "apply_clearance": "Clearance iyyadhu", "my_requests": "Gaaffiiwwan koo",
        "pending_reviews": "Eegaa jiran", "admin_panel": "Paanaalii Bulchaa",
        "departments": "Dhaabbilee", "analytics": "Xiinxala",
        "notifications": "Beeksisa", "profile": "Profaayilii",
        "students": "Barattoota", "staff": "Hojjettoota",
        "approve": "Mirkaneessi", "reject": "Kufeessi",
        "submit": "Galchi", "cancel": "Dhiisi",
    },
}

LANGUAGES = {"en": "English", "am": "አማርኛ", "om": "Afaan Oromoo"}


def get_lang():
    return session.get("lang", "en")


def translate(key):
    lang = get_lang()
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["en"].get(key, key))


def set_lang(lang):
    if lang in LANGUAGES:
        session["lang"] = lang