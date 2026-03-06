# EECS-3311 Consultant Booking Platform

A Flask + SQLite web app where clients book consultants, consultants manage schedules, and admins oversee the platform.

🔗 **Repo:** https://github.com/bensont2/EECS-3311-Consultant

---

## Architecture Overview

The app is split into four layers:

| Layer | Files | Responsibility |
|---|---|---|
| **Data** | `models.py`, `database.py`, `config.py` | ORM models, DB seeding, config |
| **Routes** | `app.py`, `routes/*.py` | URL handling, session auth |
| **Business Logic** | `services/`, `patterns/` | Booking states, payments, user creation |
| **Frontend** | `templates/` | Jinja2 HTML templates |

Flask **Blueprints** separate the three user roles (`/auth`, `/client`, `/consultant`, `/admin`). Routes are thin — all logic lives in `services/`.

---

## Design Patterns

| Pattern | File | Where It's Used |
|---|---|---|
| **Factory** | `patterns/user_factory.py` | `UserFactory.create_user()` called in `routes/auth.py` on registration — creates the right `Client`, `Consultant`, or `Admin` object based on role |
| **State** | `patterns/booking_state.py` | `transition_booking(booking, action)` in `services/booking_service.py` — enforces the booking lifecycle: `Requested → Confirmed → Paid → Completed` |
| **Strategy** | `patterns/payment_strategy.py` | `execute_transaction()` in `services/payment_service.py` — swaps between Credit Card, PayPal, and Bank Transfer strategies at runtime |

---

## How to Run

```bash
git clone https://github.com/bensont2/EECS-3311-Consultant.git
cd EECS-3311-Consultant
pip install flask flask-sqlalchemy werkzeug
python app.py
```

Visit **http://localhost:5000** — the database is created and seeded automatically.

**Test credentials:**

| Role | Email | Password |
|---|---|---|
| Admin | `admin@platform.com` | `admin123` |
| Client | `client1@test.com` | `password123` |
| Consultant | `alice@test.com` | `password123` |

---

## Team Contributions

> Full history: https://github.com/bensont2/EECS-3311-Consultant/commits/main

| Person | Role | Files |
|---|---|---|
| **Faiyaz Saraf** | Backend Core | `models.py`, `database.py`, `config.py` |
| **Abror Khabibov** | Routes / API | `app.py`, `routes/` |
| **Benson Tran** | Business Logic | `services/`, `patterns/` |
| **Misha Varankesh** | Frontend | `templates/` |
