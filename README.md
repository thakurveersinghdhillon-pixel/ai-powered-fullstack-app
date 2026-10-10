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
│   │   ├── api/v1/               # Domain endpoints (health check, API routes)
│   │   ├── core/                 # Config, Pydantic settings & DB engine session generator
│   │   ├── models/               # SQLAlchemy ORM Models (User, Conversation, Message, PromptTemplate, AIUsageRecord)
│   │   ├── schemas/              # Pydantic v2 validation schemas
│   │   └── main.py               # FastAPI application entrypoint
│   ├── alembic/                  # Database migration scripts & versions
│   ├── tests/                    # pytest test suite (models, schemas, health)
│   ├── requirements.txt
│   └── pytest.ini
├── docker-compose.yml            # PostgreSQL development service
├── .env.example                  # Environment variable blueprint
├── .gitignore                    # Git exclusions
└── README.md                     # Project setup & usage guide
```

---

## 3. Database & Migrations (Phase 2A)

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

## 4. Component Setup & Execution

### 4.1 PostgreSQL Database Service
Start the PostgreSQL container:
```bash
docker compose up -d
```

Check container status and healthcheck:
```bash
docker compose ps
```

Stop the PostgreSQL container:
```bash
docker compose down
```

### 4.2 Backend (FastAPI) Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate virtual environment and install dependencies:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the development backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Verify Health Endpoint:
   * Open `http://localhost:8000/health` or `http://localhost:8000/api/v1/health` in your browser.

### 4.3 Frontend (Next.js) Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```

2. Start the Next.js development server:
   ```bash
   npm run dev
   ```

3. Test production build:
   ```bash
   npm run build
   ```

---

## 5. Testing & Verification

### Run Backend Tests (pytest)
```bash
cd backend
./venv/bin/pytest
```

---

## 6. Project Roadmap Overview

* **Phase 0**: Architecture and Project Planning — *[Completed]*
* **Phase 1**: Project Foundation & Skeleton Setup — *[Completed]*
* **Phase 2A**: PostgreSQL Integration, ORM Models & Migrations — *[Completed]*
* **Phase 2B**: Authentication & User Management — *[Pending]*
* **Phase 3**: Conversation, Message & Template Management — *[Pending]*
* **Phase 4**: LLM Integration, SSE Streaming & Fallback Pipeline — *[Pending]*
* **Phase 5**: Next.js Chat UI & Interactive Real-Time Experience — *[Pending]*
* **Phase 6**: Cost Tracking, Dockerization & E2E Testing — *[Pending]*
