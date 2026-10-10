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
│   │   │       ├── conversations.py # Conversations & Messages API endpoints
│   │   │       ├── templates.py  # Prompt Templates API endpoints
│   │   │       └── health.py     # System health check router
│   │   ├── core/                 # Settings & security utilities
│   │   ├── models/               # SQLAlchemy ORM Models (User, RefreshSession, Conversation, Message, PromptTemplate, AIUsageRecord)
│   │   ├── schemas/              # Pydantic v2 validation schemas
│   │   └── main.py               # FastAPI application entrypoint
│   ├── alembic/                  # Database migration scripts & versions
│   ├── tests/                    # pytest test suite (auth, conversations, messages, templates, models, schemas, health)
│   ├── requirements.txt
│   └── pytest.ini
├── docker-compose.yml            # PostgreSQL development service
├── .env.example                  # Environment variable blueprint
├── .gitignore                    # Git exclusions
└── README.md                     # Project setup & usage guide
```

---

## 3. API Endpoints Specification

All protected endpoints require an `Authorization: Bearer <access_token>` header.

### 3.1 Authentication Router (`/api/v1/auth`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Register user with normalized email & Argon2id hash |
| `POST` | `/api/v1/auth/login` | Public | Authenticate user, issue access token & set HttpOnly refresh cookie |
| `POST` | `/api/v1/auth/refresh` | Cookie | Rotate refresh token & issue new access token |
| `POST` | `/api/v1/auth/logout` | Cookie | Revoke refresh session & clear cookie |
| `GET` | `/api/v1/auth/me` | Protected | Fetch current user profile |

### 3.2 Conversations & Messages Router (`/api/v1/conversations`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/conversations` | Protected | Create a new conversation |
| `GET` | `/api/v1/conversations` | Protected | List user's conversations (paginated) |
| `GET` | `/api/v1/conversations/{id}` | Protected | Retrieve a conversation by ID |
| `PATCH` | `/api/v1/conversations/{id}` | Protected | Update conversation title |
| `DELETE` | `/api/v1/conversations/{id}` | Protected | Delete conversation and cascade-delete messages |
| `POST` | `/api/v1/conversations/{id}/messages` | Protected | Save a user message (`role: "user"`) |
| `GET` | `/api/v1/conversations/{id}/messages` | Protected | List message history (paginated, `created_at ASC`) |
| `GET` | `/api/v1/conversations/{id}/messages/{msg_id}` | Protected | Retrieve an individual message |

#### Example Request: Create Conversation
```json
POST /api/v1/conversations
Headers: { "Authorization": "Bearer <access_token>" }
Body:
{
  "title": "Python Full-Stack Architecture"
}
```
#### Example Response: Create Conversation
```json
{
  "id": "b7e289f1-7c91-4d1a-9f12-9c12a83f9401",
  "user_id": "040a8b16-0961-4b8d-bc5e-70f77bb5a661",
  "title": "Python Full-Stack Architecture",
  "created_at": "2026-10-11T01:05:00Z",
  "updated_at": "2026-10-11T01:05:00Z"
}
```

#### Example Request: Save User Message
```json
POST /api/v1/conversations/b7e289f1-7c91-4d1a-9f12-9c12a83f9401/messages
Headers: { "Authorization": "Bearer <access_token>" }
Body:
{
  "role": "user",
  "content": "Explain async SQLAlchemy 2.x session management.",
  "structured_output": { "topic": "ORM", "framework": "SQLAlchemy" }
}
```

---

### 3.3 Prompt Templates Router (`/api/v1/templates`)

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/templates` | Protected | Create a reusable prompt template |
| `GET` | `/api/v1/templates` | Protected | List user's templates (paginated) |
| `GET` | `/api/v1/templates/{id}` | Protected | Retrieve a template by ID |
| `PATCH` | `/api/v1/templates/{id}` | Protected | Update template (auto-increments version on content edit) |
| `DELETE` | `/api/v1/templates/{id}` | Protected | Delete a template |

#### Example Request: Create Prompt Template
```json
POST /api/v1/templates
Headers: { "Authorization": "Bearer <access_token>" }
Body:
{
  "name": "Code Reviewer",
  "description": "Reviews Python code snippets for performance",
  "template_content": "Review the following {{language}} code: {{code}}",
  "version": 1
}
```

---

## 4. Interactive API Documentation

FastAPI automatically serves interactive Swagger and ReDoc documentation:
* **Swagger UI**: `http://localhost:8000/docs`
* **ReDoc UI**: `http://localhost:8000/redoc`
* **OpenAPI Schema**: `http://localhost:8000/api/v1/openapi.json`

---

## 5. Component Setup & Execution

### 5.1 PostgreSQL Database Service
Start the PostgreSQL container:
```bash
docker compose up -d
```

### 5.2 Backend (FastAPI) Setup
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 5.3 Frontend (Next.js) Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 6. Testing & Verification

Run the full automated test suite (33 tests covering Auth, Conversations, Messages, Templates, Models, Schemas, Health):
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
* **Phase 3**: Conversation, Message & Template Management — *[Completed]*
* **Phase 4**: LLM Integration, SSE Streaming & Fallback Pipeline — *[Pending]*
* **Phase 5**: Next.js Chat UI & Interactive Real-Time Experience — *[Pending]*
* **Phase 6**: Cost Tracking, Dockerization & E2E Testing — *[Pending]*
