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
│   └── ARCHITECTURE.md           # Phase 0 & Phase 1 Master Architecture Spec
├── frontend/                     # Next.js 15 App Router Frontend
│   ├── src/
│   │   ├── app/                  # App Router pages and layouts
│   │   ├── components/           # UI Components (Sidebar, ChatArea, MessageInput)
│   │   ├── hooks/                # Custom React Hooks
│   │   └── types/                # TypeScript interface definitions
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.ts
├── backend/                      # FastAPI Python Backend
│   ├── app/
│   │   ├── api/v1/               # Domain endpoints (health check, API routes)
│   │   ├── core/                 # Config & Pydantic settings
│   │   └── main.py               # FastAPI application entrypoint
│   ├── tests/                    # pytest test suite
│   ├── requirements.txt
│   └── pytest.ini
├── docker-compose.yml            # PostgreSQL development service
├── .env.example                  # Environment variable blueprint
├── .gitignore                    # Git exclusions
└── README.md                     # Project setup & usage guide
```

---

## 3. Environment Variable Configuration

1. Copy `.env.example` to `.env` in the root directory:
   ```bash
   cp .env.example .env
   ```
2. Key environment variables configured:
   * `POSTGRES_USER`: PostgreSQL database username (default: `postgres`)
   * `POSTGRES_PASSWORD`: PostgreSQL database password
   * `POSTGRES_DB`: PostgreSQL database name (`ai_app_db`)
   * `POSTGRES_PORT`: Exposed host port (`5434`)
   * `DATABASE_URL`: `postgresql+asyncpg://postgres:postgres_dev_password@localhost:5434/ai_app_db`
   * `NEXT_PUBLIC_API_URL`: `http://localhost:8000/api/v1`

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
1. Navigate to the backend directory and create a Python virtual environment:
   ```bash
   cd backend
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   * macOS / Linux:
     ```bash
     source venv/bin/activate
     ```
   * Windows:
     ```bash
     .\venv\Scripts\activate
     ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. Verify Health Endpoint:
   * Open `http://localhost:8000/health` or `http://localhost:8000/api/v1/health` in your browser.

### 4.3 Frontend (Next.js) Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

4. Open the application:
   * Navigate to `http://localhost:3000` in your web browser.

5. Test production build:
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

### Verify Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 6. Project Roadmap Overview

* **Phase 0**: Architecture and Project Planning — *[Completed]*
* **Phase 1**: Project Foundation & Skeleton Setup — *[Completed]*
* **Phase 2**: Database ORM Models & Authentication System — *[Pending]*
* **Phase 3**: Conversation, Message & Template Management — *[Pending]*
* **Phase 4**: LLM Integration, SSE Streaming & Fallback Pipeline — *[Pending]*
* **Phase 5**: Next.js Chat UI & Interactive Real-Time Experience — *[Pending]*
* **Phase 6**: Cost Tracking, Dockerization & E2E Testing — *[Pending]*
