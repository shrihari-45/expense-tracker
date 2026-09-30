# 💸 SpendWise AI — Smart Expense & Financial Intelligence Platform

SpendWise AI is a modern full-stack personal finance and expense tracking platform powered by **FastAPI**, **React + Vite**, and **Supabase** (PostgreSQL + Auth + Row Level Security), equipped with an intelligent AI financial engine.

---

## ✨ Features

- 📊 **Interactive Financial Dashboard**: Dynamic metric cards (total balance, monthly spending, active budgets), real-time category distribution, and spending trends.
- 💳 **Transaction Management**: User-isolated expense tracking with quick categorization, search, filtering, and pagination.
- 🎯 **Budget Ceilings & Alerts**: Set category-specific budget limits with real-time visual progress bars and overspending warnings.
- 🤖 **AI Financial Intelligence Engine**:
  - Automatic category prediction from transaction descriptions.
  - Automated anomaly detection & spending spike alerts.
  - Contextual financial chat assistant for personalized savings tips.
- 🔐 **Robust Authentication**: Supabase Auth integration with secure JWT verification and Row-Level Security (RLS) policies.

---

## 🛠️ Tech Stack

- **Frontend**: React 19, Vite, TailwindCSS, Lucide Icons, Recharts, Axios
- **Backend**: FastAPI, Uvicorn, Pydantic v2, Supabase-py, PyJWT
- **Database & Auth**: Supabase (PostgreSQL, Row Level Security, Auth triggers)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ & npm

### 1. Clone the Repository
```bash
git clone https://github.com/shrihari-45/expense-tracker.git
cd expense-tracker
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Provide your Supabase URL and Key in `.env`:
```env
HOST=127.0.0.1
PORT=5000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-key
```

### 3. Setup Backend
```bash
pip install -r requirements.txt
python run.py
```
- API Base: `http://127.0.0.1:5000`
- Interactive Swagger UI: `http://127.0.0.1:5000/docs`

### 4. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📄 License
MIT
