# SpendWise AI — Backend Architecture & Integration Guide

SpendWise AI is powered by a high-performance **FastAPI** backend and **Supabase** (PostgreSQL + Auth + Row-Level Security), featuring an integrated AI financial intelligence engine.

---

## 🏗️ Architecture Overview

```
c:\expence_tracker\
├── app/
│   ├── api/
│   │   ├── deps.py               # get_current_user dependency (Supabase JWT / Auth verification)
│   │   └── v1/
│   │       ├── __init__.py       # Aggregated v1 API router
│   │       ├── auth.py           # Register, Login, Me, Token verification
│   │       ├── expenses.py       # Expense CRUD with filter, search, sort & user isolation
│   │       ├── budgets.py        # Category ceiling budget upsert & retrieval
│   │       └── ai.py             # Categorize, Insights, Contextual Chat endpoints
│   ├── core/
│   │   ├── config.py             # Pydantic v2 BaseSettings loading .env & CORS
│   │   ├── supabase.py           # Reusable Supabase client initialization
│   │   └── db.py                 # Development in-memory fallback & JWT generation
│   ├── schemas/
│   │   ├── __init__.py           # Unified exports
│   │   ├── auth.py               # UserRegister, UserLogin, AuthResponse, UserResponse
│   │   ├── expense.py            # ExpenseCreate, ExpenseUpdate, ExpenseResponse
│   │   ├── budget.py             # BudgetCreate, BudgetResponse
│   │   └── ai.py                 # CategorizeRequest, InsightsResponse, ChatRequest, ChatResponse
│   ├── services/
│   │   └── ai_service.py         # AI Auto-categorizer, anomaly detector, insights & chat engine
│   └── main.py                   # FastAPI application, CORS middleware, lifespan & routing
├── supabase_schema.sql           # Complete Supabase SQL migration with RLS & triggers
├── requirements.txt              # Production Python dependencies
├── .env.example                  # Environment template
├── .env                          # Local environment settings
├── run.py                        # Uvicorn server launcher
└── test_backend.py               # Complete automated test suite
```

---

## ⚡ Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Fill in your Supabase credentials in [`.env`](file:///c:/expence_tracker/.env):
```env
HOST=127.0.0.1
PORT=5000

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret

# Optional for external LLM querying (fallback rule engine is built-in)
GEMINI_API_KEY=
OPENAI_API_KEY=
```

### 3. Run Database Migration in Supabase
Copy the SQL from [`supabase_schema.sql`](file:///c:/expence_tracker/supabase_schema.sql) and execute it in your **Supabase Dashboard -> SQL Editor**:
- Creates `expenses` & `budgets` tables.
- Sets foreign keys to `auth.users(id)` with cascade deletion.
- Enforces strict Row Level Security (RLS) policies.
- Automatically generates indexes and timestamp triggers.

### 4. Start the Backend Server
```bash
python run.py
```
Or with Uvicorn:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 5000 --reload
```

- API Base: `http://127.0.0.1:5000`
- Interactive Swagger Docs: `http://127.0.0.1:5000/docs`
- ReDoc Docs: `http://127.0.0.1:5000/redoc`

### 5. Start the React Frontend
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📡 API Endpoints

### 🔐 Authentication (`/api/auth`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new user via Supabase Auth |
| `POST` | `/api/auth/login` | Authenticate user, receive JWT Bearer token |
| `GET` | `/api/auth/me` | Retrieve authenticated user profile |
| `GET` | `/api/auth/verify` | Validate current JWT session token |

### 💳 Expense CRUD (`/api/expenses`)
| Method | Endpoint | Query / Body | Description |
|---|---|---|---|
| `GET` | `/api/expenses` | `category`, `search`, `sort` | List expenses (user-isolated, searchable, sortable) |
| `POST` | `/api/expenses` | `ExpenseCreate` | Create transaction record (`user_id` enforced) |
| `PUT` | `/api/expenses/{id}` | `ExpenseUpdate` | Update user's transaction |
| `DELETE` | `/api/expenses/{id}`| - | Delete user's transaction |

### 🎯 Budgets (`/api/budgets`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/budgets` | List user's category budget ceilings |
| `POST` | `/api/budgets` | Upsert ceiling limit per category |

### 🤖 AI Financial Engine (`/api/ai`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/ai/categorize` | Predict category (Food, Transport, Shopping, etc.) from title |
| `POST` | `/api/ai/insights` | Anomaly detection, category spikes, budget guardrails & savings tips |
| `POST` | `/api/ai/chat` | Contextual queries ("Where did I spend most?", "Save 20% on shopping") |

---

## 🧪 Automated Testing
Run the comprehensive test suite verifying all 12 endpoints:
```bash
python test_backend.py
```
