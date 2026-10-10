# AI-Powered Full-Stack Application

An AI-powered full-stack application built with **Next.js 15 (TypeScript)**, **FastAPI (Python 3.12+)**, **PostgreSQL**, **LLM APIs**, and **Docker**.

---

## 1. Prerequisites

Before setting up the project, ensure you have the following installed:
* **Node.js**: `v20.x` or higher
* **npm**: `v10.x` or higher
* **Python**: `3.11`, `3.12`, `3.13`, or `3.14`
* **Docker Desktop**: Docker version `20.10+` with Compose support
* **Git**: `2.x+`

---

## 2. Project Structure

```
ai-powered-fullstack-app/
├── docs/
│   └── ARCHITECTURE.md           # Master Architecture & Phase Specification
├── frontend/                     # Next.js 15 App Router Frontend
│   ├── src/
│   │   ├── app/                  # App Router pages and layouts
│   │   ├── components/           # UI Components (Sidebar, ChatArea, MessageInput)
│   │   └── types/                # TypeScript interface definitions
│   ├── package.json
│   └── tailwind.config.ts
├── backend/                      # FastAPI Python Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py           # FastAPI dependency for JWT current user validation
│   │   │   └── v1/
│   │   │       ├── auth.py       # Authentication endpoints (register, login, refresh, logout, me)
│   │   │       └── health.py     # System health check router
│   │   ├── core/                 # Settings & Argon2id/JWT security utilities
│   │   ├── models/               # SQLAlchemy ORM Models (User, RefreshSession, Conversation, Message, etc.)
│   │   ├── schemas/              # Pydantic v2 validation schemas
│   │   └── main.py               # FastAPI application entrypoint
│   ├── alembic/                  # Database migration scripts & versions
│   ├── tests/                    # pytest test suite (auth, models, schemas, health)
│   ├── requirements.txt
│   └── pytest.ini
├── docker-compose.yml            # PostgreSQL development service
├── .env.example                  # Environment variable blueprint
├── .gitignore                    # Git exclusions
└── README.md                     # Project setup & usage guide
```

---

## 3. Authentication & API Specification (Phase 2B)

### Endpoints Overview

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Registers a new user with normalized email & Argon2id password hashing |
| `POST` | `/api/v1/auth/login` | Public | Authenticates credentials, issues access token & sets HttpOnly refresh cookie |
| `POST` | `/api/v1/auth/refresh` | Public (Cookie) | Rotates refresh token & issues new access token (with replay attack detection) |
| `POST` | `/api/v1/auth/logout` | Public (Cookie) | Revokes server-side refresh session & clears HttpOnly cookie |
| `GET` | `/api/v1/auth/me` | Protected | Returns authenticated user profile (requires `Authorization: Bearer <token>`) |

### Development Cookie & CORS Notes
* **Local HTTP Development**: `COOKIE_SECURE=False` in `.env` for local HTTP cookie transmission.
* **Production HTTPS**: `COOKIE_SECURE=True` in production environment variables over TLS/HTTPS.
* **CORS**: Configured with strict origin checks (`http://localhost:3000`) and `allow_credentials=True`.

---

## 4. Database & Migrations

### Database Migrations (Alembic)
Apply database migrations to PostgreSQL:
```bash
cd backend
./venv/bin/alembic upgrade head
```

Generate new migration:
```bash
cd backend
./venv/bin/alembic revision --autogenerate -m "migration_description"
```

---

## 5. Component Setup & Execution

### 5.1 PostgreSQL Database Service
Start the PostgreSQL container:
```bash
docker compose up -d
```

Check container status and healthcheck:
```bash
docker compose ps
```

### 5.2 Backend (FastAPI) Setup
1. Navigate to backend directory and activate virtual environment:
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run development backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

3. Open Swagger API Documentation:
   * Navigate to `http://localhost:8000/api/v1/openapi.json` or interactive docs.

### 5.3 Frontend (Next.js) Setup
1. Navigate to frontend directory and run dev server:
   ```bash
   cd frontend
   npm run dev
   ```

---

## 6. Testing & Verification

### Run Backend Tests (pytest)
```bash
cd backend
./venv/bin/pytest
```

---

## 7. Project Roadmap Overview

* **Phase 0**: Architecture and Project Planning — *[Completed]*
* **Phase 1**: Project Foundation & Skeleton Setup — *[Completed]*
* **Phase 2A**: PostgreSQL Integration, ORM Models & Migrations — *[Completed]*
* **Phase 2B**: Authentication & User Management — *[Completed]*
* **Phase 3**: Conversation, Message & Template Management — *[Pending]*
* **Phase 4**: LLM Integration, SSE Streaming & Fallback Pipeline — *[Pending]*
* **Phase 5**: Next.js Chat UI & Interactive Real-Time Experience — *[Pending]*
* **Phase 6**: Cost Tracking, Dockerization & E2E Testing — *[Pending]*
