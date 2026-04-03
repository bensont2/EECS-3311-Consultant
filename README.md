# EECS-3311 Consultant Booking Platform

A Flask + SQLite web app where clients book consultants, consultants manage schedules, and admins oversee the platform. Now with AI-powered Customer Assistant and Docker deployment.

🔗 **Repo:** https://github.com/bensont2/EECS-3311-Consultant

---

## Phase Overview

### Phase 1: Core System Architecture
- User authentication and role-based access (Client, Consultant, Admin)
- Booking system with state management
- Payment processing with multiple strategies
- Basic frontend templates

### Phase 2: Frontend Completion, Deployment & AI Integration
- ✅ Complete frontend implementation for all user workflows
- ✅ Docker-based deployment (3+ containers)
- ✅ AI-powered Customer Assistant chatbot integration
- ✅ Full system deployment with docker-compose

---

## Architecture Overview

The app is split into four layers:

| Layer | Files | Responsibility |
|---|---|---|
| **Data** | `models.py`, `database.py`, `config.py` | ORM models, DB seeding, config |
| **Routes** | `app.py`, `routes/*.py` | URL handling, session auth |
| **Business Logic** | `services/`, `patterns/` | Booking states, payments, user creation |
| **Frontend** | `templates/` | Jinja2 HTML templates |
| **AI Assistant** | `ai_service/` | Chatbot integration with LLM backend |

Flask **Blueprints** separate the three user roles (`/auth`, `/client`, `/consultant`, `/admin`). Routes are thin — all logic lives in `services/`.

---

## Design Patterns

| Pattern | File | Where It's Used |
|---|---|---|
| **Factory** | `patterns/user_factory.py` | `UserFactory.create_user()` called in `routes/auth.py` on registration — creates the right `Client`, `Consultant`, or `Admin` object based on role |
| **State** | `patterns/booking_state.py` | `transition_booking(booking, action)` in `services/booking_service.py` — enforces the booking lifecycle: `Requested → Confirmed → Paid → Completed` |
| **Strategy** | `patterns/payment_strategy.py` | `execute_transaction()` in `services/payment_service.py` — swaps between Credit Card, PayPal, and Bank Transfer strategies at runtime |

---

## Phase 2 Features

### 1. Frontend Completion

**Client Features:**
- Browse available consulting services
- Request and manage bookings
- Cancel bookings and view history
- Process payments and manage payment methods
- View payment history
- Access AI Customer Assistant chatbot

**Consultant Features:**
- Manage availability and schedule
- Accept or reject booking requests
- View complete booking schedule
- Profile management

**Admin Features:**
- Approve new consultant registrations
- View system status and analytics
- Manage system policies
- Monitor platform activity

### 2. Docker-Based Deployment

The system is deployed using Docker with the following containers:

- **Backend Service Container** - Flask API server
- **Frontend Service Container** - Web interface (or served by backend)
- **Database Container** - SQLite persistence with volume mounting
- **Docker Compose** - Orchestrates all services with a single command

**Single Command Deployment:**
```bash
docker-compose up
```

All services are properly networked, databases persist using volumes, and environment variables are configured through `.env` files.

### 3. AI Customer Assistant

The platform includes an AI-powered chatbot accessible to clients that:
- Answers questions about the consulting platform
- Provides information about available services and consultants
- Explains the booking process
- Details payment methods and policies
- Assists with troubleshooting
- Guides users through platform features

**Privacy & Safety:**
- AI has no direct database access
- Only general platform information is provided to the AI
- No personal user data, payment details, or private booking information is shared
- AI responses are informative and provide guidance, not automated actions

**Access the Chatbot:**
Navigate to the client dashboard and click "AI Assistant" in the sidebar. The chatbot interface appears in a modal where you can ask questions about the platform.

---

## How to Run

### Option 1: Docker Deployment (Recommended)

```bash
git clone https://github.com/bensont2/EECS-3311-Consultant.git
cd EECS-3311-Consultant

# Copy environment template
cp .env.example .env
# Edit .env with your API keys (see .env.example for required variables)

# Start all services
docker-compose up

```

Visit **http://localhost:5000** — the system will be fully initialized.

### Option 2: Local Development

```bash
git clone https://github.com/bensont2/EECS-3311-Consultant.git
cd EECS-3311-Consultant
pip install -r requirements.txt
python Backend/app.py
```

Visit **http://localhost:5000** — the database is created and seeded automatically.

---

## Test Credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@platform.com` | `admin123` |
| Client | `client1@test.com` | `password123` |
| Consultant | `alice@test.com` | `password123` |

---

## Project Structure

```
EECS-3311-Consultant/
├── Backend/
│   ├── app.py                    # Flask application entry point
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── database.py               # Database initialization and seeding
│   ├── config.py                 # Configuration settings
│   ├── routes/                   # Blueprint routes
│   │   ├── auth.py
│   │   ├── client.py
│   │   ├── consultant.py
│   │   ├── admin.py
│   │   └── ai_assistant.py       # AI chatbot routes
│   ├── services/                 # Business logic
│   │   ├── booking_service.py
│   │   ├── payment_service.py
│   │   ├── user_service.py
│   │   └── ai_service.py         # AI integration logic
│   ├── patterns/                 # Design patterns
│   │   ├── user_factory.py
│   │   ├── booking_state.py
│   │   └── payment_strategy.py
│   ├── ai_service/               # AI assistant implementation
│   │   ├── llm_provider.py       # LLM API integration
│   │   └── chatbot.py            # Chatbot logic
│   ├── templates/                # Jinja2 HTML templates
│   ├── static/                   # CSS, JavaScript, images
│   ├── Dockerfile                # Backend container
│   └── requirements.txt           # Python dependencies
├── docker-compose.yml            # Multi-container orchestration
├── .env.example                  # Environment variables template
├── .gitignore
└── README.md                     # This file
```

---

## Team Contributions

### Phase 1

| Person | Role | Contributions |
|---|---|---|
| **Faiyaz Saraf** | Backend Core | `models.py`, `database.py`, `config.py` |
| **Abror Khabibov** | Routes / API | `app.py`, `routes/`, API endpoints |
| **Benson Tran** | Business Logic | `services/`, `patterns/`, state management |
| **Misha Varankesh** | Frontend | `templates/`, UI/UX |

### Phase 2

| Person | Role | Key Contributions |
|---|---|---|
| **Faiyaz Saraf** | AI Assistant Integration | AI service implementation, LLM provider integration, chatbot logic |
| **Benson Tran** | Docker & AI Assistant | Docker setup, docker-compose configuration, AI assistant backend integration |
| **Misha Varankesh** | Frontend Completion | Frontend UI completion, responsive design, AI chatbot interface |
| **Abror Khabibov** | Frontend Completion | Frontend workflows, routing, integration with backend APIs |

> Full commit history: https://github.com/bensont2/EECS-3311-Consultant/commits/main


## AI Assistant Documentation

The AI Customer Assistant is fully documented in `AI_CHATBOT_DOCUMENTATION.md`, including:
- Chatbot functionality overview
- Example questions and responses
- System context provided to the AI
- Privacy and safety measures
- API integration approach

---

## Troubleshooting

**Docker containers not starting?**
- Ensure Docker and Docker Compose are installed
- Check that ports 5000 (backend), 3000 (frontend), and 5432 (database) are available
- Review logs: `docker-compose logs -f`

**AI Assistant not responding?**
- Verify API key is correctly set in `.env`
- Check AI service logs: `docker-compose logs ai_service`
- Ensure internet connectivity for LLM API calls

**Database not persisting?**
- Verify volumes are mounted in docker-compose.yml
- Check directory permissions for data persistence

---

## Resources

- [Design Patterns: Elements of Reusable Object-Oriented Software](https://en.wikipedia.org/wiki/Design_Patterns) by Gang of Four
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [OpenAI API](https://openai.com/api/) / [Claude API](https://www.anthropic.com/api) / [Gemini API](https://ai.google.dev/)

---

## License

EECS 3311 Course Project
