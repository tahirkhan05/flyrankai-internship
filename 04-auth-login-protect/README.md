# Supabase Auth: Login & Protect

FlyRank Internship Backend Track · Week 2 · Assignment A4

Build a secure API with **Supabase Auth** — user registration, login, logout, JWT verification, and protected routes using FastAPI.

---

## Stage 0: Setup Server & Supabase Client

### 1. Requirements
Install dependencies:
```bash
pip install fastapi uvicorn supabase python-dotenv
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and fill in your Supabase credentials:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
PORT=8000
```

### 3. Run the Server
```bash
uvicorn main:app --reload
```

