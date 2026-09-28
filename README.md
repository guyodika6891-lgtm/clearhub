<<<<<<< HEAD
# 🎓 ClearHub — University Digital Clearance System

A modern, AI-powered clearance workflow platform for universities. Students apply online, departments approve digitally, and certificates generate automatically — no more walking between offices.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-ClearHub-2563eb?style=for-the-badge&logo=render)](https://clearhub-8w1o.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=flat-square&logo=bootstrap)](https://getbootstrap.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 🌐 Live Demo

👉 **[https://clearhub-8w1o.onrender.com](https://clearhub-8w1o.onrender.com)**

> ⏱️ **First request may take 30 seconds** — Render's free tier sleeps after inactivity. Just refresh once and it wakes up.

---

## ✨ Features

### 👥 Multi-Role Platform
- 👑 **Admin** — manage users, departments, semesters, and analytics
- 👨‍🏫 **Staff** — review and approve their department's steps
- 🎓 **Student** — apply, track, upload documents, earn certificates

### 🏛️ Complete University Workflow
- **16 departments** — Library, Finance, Cafeteria, Hospital, Dormitory, Security, ICT, Registrar, and more
- **Sequential approval** — each department reviews in order
- **Document uploads** — receipts, letters, IDs
- **Auto-issued PDF certificates** with QR codes

### 🤖 AI-Powered Assistant
- Ask *"Why is my clearance stuck?"* → gets real answers from your data
- Uses OpenAI GPT-4o-mini
- Context-aware per user role (student / staff / admin)

### 📱 Modern Experience
- **QR code verification** — scan any certificate for public status
- **Real-time notifications** — Socket.IO push updates
- **Multi-language** — English · አማርኛ · Afaan Oromoo
- **4 theme modes** — Light · Dark · Neumorphic · High Contrast
- **PWA installable** — works offline on phone
- **Premium animations** — page transitions, custom cursor, morphing cards

### 📊 Analytics & Reporting
- **Bottleneck detection** — which departments are slowest
- **Department heatmap** — pending load visualization
- **30-day trends** — Chart.js graphs
- **CSV exports** — 1-click admin reports
- **Stalled request alerts** — flag overdue steps

### 💳 Payments & Chat
- **Stripe integration** — pay clearance fees online
- **Per-request chat** — staff ↔ student messaging
- **Email notifications** — auto-sent on every status change

### 🔒 Enterprise Security
- PBKDF2 password hashing
- CSRF protection on all forms
- Rate limiting (login, register, uploads)
- Account lockout after 5 failed attempts
- Content Security Policy headers
- Secure HttpOnly SameSite cookies
- MIME-type verification on uploads
- Audit logging of every action
- Role-based access control

---

## 📸 Screenshots

### 🏠 Homepage — Animated Hero
![Homepage](screenshots/homepage.png)

### 🔐 Login — Neumorphic Design
![Login](screenshots/login.png)

### 📊 Student Dashboard
![Student Dashboard](screenshots/student-dashboard.png)

### 📋 Clearance Detail with QR + Chat
![Clearance Detail](screenshots/clearance-detail.png)

### 👨‍🏫 Staff Review Page
![Staff Review](screenshots/staff-review.png)

### 👑 Admin Panel
![Admin Panel](screenshots/admin-panel.png)

### 🔥 Department Heatmap
![Heatmap](screenshots/heatmap.png)

### 📜 PDF Certificate
![Certificate](screenshots/certificate.png)

### 🤖 AI Assistant
![AI Assistant](screenshots/ai-chat.png)

### 🌙 Dark Mode
![Dark Mode](screenshots/dark-mode.png)

> 📝 *Upload your screenshots to the `screenshots/` folder to display them here.*

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11 · Flask 3 · SQLAlchemy |
| **Auth** | Flask-Login · Werkzeug (PBKDF2) |
| **Forms** | Flask-WTF · WTForms |
| **Real-time** | Flask-SocketIO · eventlet |
| **AI** | OpenAI GPT-4o-mini |
| **PDF** | ReportLab · qrcode |
| **Payments** | Stripe |
| **Email** | Flask-Mail |
| **Security** | Flask-Limiter · Flask-Talisman |
| **Frontend** | Bootstrap 5.3 · Bootstrap Icons · Chart.js |
| **Database** | SQLite (dev) · PostgreSQL (production) |
| **Deploy** | Render · Gunicorn |

---

## 🚀 Run Locally

```bash
# 1. Clone
git clone https://github.com/guyodika6891-lgtm/clearhub.git
cd clearhub

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux

# 5. Run
python app.py
=======
# 🎓 ClearHub — University Digital Clearance System

A modern, AI-powered clearance workflow platform for universities. Students apply online, departments approve digitally, and certificates generate automatically — no more walking between offices.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-ClearHub-2563eb?style=for-the-badge&logo=render)](https://clearhub-8w1o.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=flat-square&logo=bootstrap)](https://getbootstrap.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 🌐 Live Demo

👉 **[https://clearhub-8w1o.onrender.com](https://clearhub-8w1o.onrender.com)**

> ⏱️ **First request may take 30 seconds** — Render's free tier sleeps after inactivity. Just refresh once and it wakes up.

---

## ✨ Features

### 👥 Multi-Role Platform
- 👑 **Admin** — manage users, departments, semesters, and analytics
- 👨‍🏫 **Staff** — review and approve their department's steps
- 🎓 **Student** — apply, track, upload documents, earn certificates

### 🏛️ Complete University Workflow
- **16 departments** — Library, Finance, Cafeteria, Hospital, Dormitory, Security, ICT, Registrar, and more
- **Sequential approval** — each department reviews in order
- **Document uploads** — receipts, letters, IDs
- **Auto-issued PDF certificates** with QR codes

### 🤖 AI-Powered Assistant
- Ask *"Why is my clearance stuck?"* → gets real answers from your data
- Uses OpenAI GPT-4o-mini
- Context-aware per user role (student / staff / admin)

### 📱 Modern Experience
- **QR code verification** — scan any certificate for public status
- **Real-time notifications** — Socket.IO push updates
- **Multi-language** — English · አማርኛ · Afaan Oromoo
- **4 theme modes** — Light · Dark · Neumorphic · High Contrast
- **PWA installable** — works offline on phone
- **Premium animations** — page transitions, custom cursor, morphing cards

### 📊 Analytics & Reporting
- **Bottleneck detection** — which departments are slowest
- **Department heatmap** — pending load visualization
- **30-day trends** — Chart.js graphs
- **CSV exports** — 1-click admin reports
- **Stalled request alerts** — flag overdue steps

### 💳 Payments & Chat
- **Stripe integration** — pay clearance fees online
- **Per-request chat** — staff ↔ student messaging
- **Email notifications** — auto-sent on every status change

### 🔒 Enterprise Security
- PBKDF2 password hashing
- CSRF protection on all forms
- Rate limiting (login, register, uploads)
- Account lockout after 5 failed attempts
- Content Security Policy headers
- Secure HttpOnly SameSite cookies
- MIME-type verification on uploads
- Audit logging of every action
- Role-based access control

---

## 📸 Screenshots

### 🏠 Homepage — Animated Hero
![Homepage](screenshots/homepage.png)

### 🔐 Login — Neumorphic Design
![Login](screenshots/login.png)

### 📊 Student Dashboard
![Student Dashboard](screenshots/student-dashboard.png)

### 📋 Clearance Detail with QR + Chat
![Clearance Detail](screenshots/clearance-detail.png)

### 👨‍🏫 Staff Review Page
![Staff Review](screenshots/staff-review.png)

### 👑 Admin Panel
![Admin Panel](screenshots/admin-panel.png)

### 🔥 Department Heatmap
![Heatmap](screenshots/heatmap.png)

### 📜 PDF Certificate
![Certificate](screenshots/certificate.png)

### 🤖 AI Assistant
![AI Assistant](screenshots/ai-chat.png)

### 🌙 Dark Mode
![Dark Mode](screenshots/dark-mode.png)

> 📝 *Upload your screenshots to the `screenshots/` folder to display them here.*

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11 · Flask 3 · SQLAlchemy |
| **Auth** | Flask-Login · Werkzeug (PBKDF2) |
| **Forms** | Flask-WTF · WTForms |
| **Real-time** | Flask-SocketIO · eventlet |
| **AI** | OpenAI GPT-4o-mini |
| **PDF** | ReportLab · qrcode |
| **Payments** | Stripe |
| **Email** | Flask-Mail |
| **Security** | Flask-Limiter · Flask-Talisman |
| **Frontend** | Bootstrap 5.3 · Bootstrap Icons · Chart.js |
| **Database** | SQLite (dev) · PostgreSQL (production) |
| **Deploy** | Render · Gunicorn |

---

## 🚀 Run Locally

```bash
# 1. Clone
git clone https://github.com/guyodika6891-lgtm/clearhub.git
cd clearhub

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux

# 5. Run
python app.py
>>>>>>> 000e3c5a9d5be38f89900c87d60332bfac489267
