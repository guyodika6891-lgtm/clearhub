# 🎓 ClearHub — University Digital Clearance System

A modern, AI-powered clearance workflow platform for universities. Students apply online, departments approve digitally, and certificates generate automatically — no more walking between offices.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 👥 **Multi-role platform** — Admin · Department Staff · Student
- 🏛️ **16 university departments** — Library, Finance, Cafeteria, Hospital, Security, Registrar, and more
- 📝 **Sequential approval workflow** — each department reviews in order
- 📎 **Document uploads** — receipts, letters, IDs
- 🤖 **AI Assistant** — asks "why is my clearance stuck?" and gets real answers
- 📱 **QR code verification** — scan to verify any certificate publicly
- 📊 **Advanced analytics** — bottleneck detection, department heatmaps
- 📧 **Email notifications** — auto-email on every status change
- ⏰ **Deadline alerts** — flag stalled requests
- 📤 **CSV exports** — 1-click admin reports
- 🌐 **Multi-language** — English · አማርኛ · Afaan Oromoo
- 💳 **Stripe payments** — pay clearance fees online
- 💬 **Chat per request** — staff ↔ student messaging
- 📱 **PWA installable** — works offline on phone
- 🎨 **4 theme modes** — Light · Dark · Neumorphic · High Contrast
- 🔒 **Enterprise security** — CSRF, rate limiting, audit logs, secure cookies

---

## 🖥️ Run Locally

```bash
git clone https://github.com/<your-username>/clearhub.git
cd clearhub
python -m venv .venv
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Open **http://127.0.0.1:5000** — first registered user becomes **admin** 👑.

---

## 🌐 Deploy to Render

1. Push code to GitHub ✅ (you're here)
2. Go to [render.com](https://render.com) → **New → Blueprint**
3. Select your `clearhub` repo
4. Render reads `render.yaml` → click **Apply**
5. Wait ~4 minutes → done 🚀

---

## 🎯 Roles

| Role | Capabilities |
|---|---|
| 👑 **Admin** | Manage users, departments, semesters, view audit log, analytics |
| 👨‍🏫 **Staff** | Review and approve clearance steps for their department |
| 🎓 **Student** | Apply for clearance, upload documents, track progress, get certificate |

---

## 🔐 Security

- ✅ PBKDF2 password hashing
- ✅ CSRF protection on all forms
- ✅ Rate limiting (login, register, uploads)
- ✅ Account lockout after 5 failed attempts
- ✅ Content Security Policy headers
- ✅ Secure HttpOnly SameSite cookies
- ✅ MIME-type verification on uploads
- ✅ Audit logging of every action
- ✅ Role-based access control

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

## 👨‍💻 Author

**GUYO DIKA**
Lecturer at Werabe University
📧 [guyodika6891@gmail.com](mailto:guyodika6891@gmail.com)
