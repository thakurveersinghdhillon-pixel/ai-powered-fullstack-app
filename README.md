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

## 2. LLM Environment Configuration (Phase 4)

Configure LLM provider variables in `.env` (or environment variables):

```bash
# LLM Provider Configuration
OPENAI_API_KEY="sk-proj-your-openai-api-key-here"  # Leave empty or unset to use MockLLMProvider for offline testing
LLM_PROVIDER="openai"                             # Supported: "openai", "mock"
LLM_MODEL="gpt-4o-mini"                           # Target model identifier
LLM_TIMEOUT_SECONDS=30.0                          # Request/connection timeout
LLM_MAX_RETRIES=3                                 # Maximum transient retries with backoff & jitter
```

* **Offline / Testing Mode**: When `OPENAI_API_KEY` is not set, `get_llm_provider` automatically falls back to `MockLLMProvider`, enabling deterministic offline testing without paid API credentials.

---

## 3. Server-Sent Events (SSE) Streaming Protocol

### Endpoint: `POST /api/v1/conversations/{conversation_id}/messages/stream`
* **Headers Required**: `Authorization: Bearer <access_token>`
* **Response Content-Type**: `text/event-stream`
* **Response Headers**: `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no`

### SSE Event Stream Sequence

```http
event: start
data: {"user_message_id": "1c025197-3157-42b9-897c-18dd9280dd4c", "assistant_message_id": "e4ca67fd-5d62-4f32-8418-406a6442ef57", "conversation_id": "b7e289f1-7c91-4d1a-9f12-9c12a83f9401"}

event: token
data: {"content": "Space "}

event: token
data: {"content": "exploration "}

event: metadata
data: {"provider": "openai", "model": "gpt-4o-mini", "usage": {"prompt_tokens": 15, "completion_tokens": 12, "total_tokens": 27}, "structured_output": null}

event: done
data: {"status": "completed", "assistant_message_id": "e4ca67fd-5d62-4f32-8418-406a6442ef57"}
```

#### Error Handling Event
```http
event: error
data: {"error": "LLM provider rate limit exceeded", "code": "PROVIDER_ERROR"}
```

---

## 4. API Specification Summary

All protected endpoints require `Authorization: Bearer <access_token>`.

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Auth** | `POST` | `/api/v1/auth/register` | User registration (Argon2id hashing) |
| **Auth** | `POST` | `/api/v1/auth/login` | Login, JWT access token & HttpOnly refresh cookie |
| **Auth** | `POST` | `/api/v1/auth/refresh` | Rotate refresh token cookie |
| **Auth** | `POST` | `/api/v1/auth/logout` | Revoke session & clear cookie |
| **Auth** | `GET` | `/api/v1/auth/me` | Current user profile |
| **Conversations** | `POST` | `/api/v1/conversations` | Create conversation |
| **Conversations** | `GET` | `/api/v1/conversations` | List user conversations (paginated) |
| **Conversations** | `DELETE` | `/api/v1/conversations/{id}` | Delete conversation & cascade messages |
| **Messages** | `POST` | `/api/v1/conversations/{id}/messages` | Save user message (`role: "user"`) |
| **Messages** | `POST` | `/api/v1/conversations/{id}/messages/stream` | **Stream AI response tokens via SSE** |
| **Messages** | `GET` | `/api/v1/conversations/{id}/messages` | Paginated message history (`created_at ASC`) |
| **Templates** | `POST` | `/api/v1/templates` | Create prompt template (`{{topic}}` placeholders) |
| **Templates** | `PATCH` | `/api/v1/templates/{id}` | Update template (auto-increments version) |

---

## 5. Interactive API Documentation

* **Swagger UI**: `http://localhost:8000/docs`
* **ReDoc UI**: `http://localhost:8000/redoc`

---

## 6. Testing & Verification

### Backend Tests
Run the full automated backend test suite (39 tests covering LLM integration, SSE streaming, structured outputs, exponential retries, Auth, Conversations, Messages, Templates, Models, Schemas, Health):
```bash
cd backend
./venv/bin/pytest
```

### Frontend Build & Tests
Run the frontend production build and unit test suite:
```bash
cd frontend
npm run build
node src/__tests__/stream_parser.test.js
```

---

## 7. Running the Full Stack

1. **Start Backend & Database**:
```bash
cd backend
# Ensure PostgreSQL container is running on port 5434
docker compose up -d postgres
./venv/bin/uvicorn app.main:app --reload --port 8000
```

2. **Start Next.js Frontend**:
```bash
cd frontend
npm run dev
```
Navigate to `http://localhost:3000` to access the AI workspace.

---

## 8. Project Roadmap Overview

* **Phase 0**: Architecture and Project Planning — *[Completed]*
* **Phase 1**: Project Foundation & Skeleton Setup — *[Completed]*
* **Phase 2A**: PostgreSQL Integration, ORM Models & Migrations — *[Completed]*
* **Phase 2B**: Authentication & User Management — *[Completed]*
* **Phase 3**: Conversation, Message & Template Management — *[Completed]*
* **Phase 4**: LLM Integration, SSE Streaming & Fallback Pipeline — *[Completed]*
* **Phase 5**: Next.js Chat UI & Interactive Real-Time Experience — *[Completed]*
* **Phase 6**: Cost Tracking, Dockerization & E2E Testing — *[Pending]*
