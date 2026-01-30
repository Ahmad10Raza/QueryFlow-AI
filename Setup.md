# QueryFlow AI - Setup Guide

This guide covers setting up QueryFlow AI for development on **Linux** and **Windows**.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

1. **Python 3.10+**: [Download](https://www.python.org/downloads/)
2. **Node.js 18+** and **npm**: [Download](https://nodejs.org/en/download/)
3. **Docker Desktop** (optional, recommended for databases): [Download](https://www.docker.com/products/docker-desktop/)
4. **Git**: [Download](https://git-scm.com/downloads)

---

## 🏗️ Project Structure

- `backend/`: Python FastAPI application (API, AI Logic, DB Access)
- `frontend/`: Next.js application (UI, Chat Interface)

---

## 🔧 Backend Setup (Python/FastAPI)

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(If you get a permission error, run `Set-ExecutionPolicy Unrestricted -Scope Process` first)*

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory by copying the example:

**Linux:**

```bash
cp .env.example .env
```

**Windows:**

```powershell
copy .env.example .env
```

**Update `.env` with your credentials:**

```ini
# Database (MySQL Local or Docker)
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/queryflow

# MongoDB (optional, for specific features)
MONGO_DATABASE_URL=mongodb+srv://...

# Authentication
SECRET_KEY=your_super_secret_key_change_this
ALGORITHM=HS256

# LLM Providers (Ollama / OpenAI)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
# OPENAI_API_KEY=sk-... (if using OpenAI)
```

### 5. Initialize Database (Migrations)

Run Alembic to create tables:

```bash
alembic upgrade head
```

### 6. Run the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API Docs will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🎨 Frontend Setup (Next.js)

### 1. Navigate to Frontend Directory

Open a new terminal and go to the frontend folder:

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
```

### 3. Configure Environment

Create a `.env.local` file:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 4. Run the Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🐳 Database Setup (Using Docker)

If you don't have MySQL installed locally, you can spin it up quickly with Docker:

```bash
docker run --name queryflow-db -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=queryflow -p 3306:3306 -d mysql:8.0
```

Update your `.env` `DATABASE_URL`:

```ini
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/queryflow
```

---

## ❓ Troubleshooting

### 1. "Module not found" in Python

Make sure your virtual environment is activated (`(venv)` should appear in your terminal prompt).

### 2. Frontend Connection Refused

Ensure the backend is running on port 8000. Check console logs in the browser (F12) for network errors.

### 3. Database Connection Error

- Verify Docker container is running: `docker ps`
- Check username/password in `.env`
- Ensure port 3306 is not occupied by another service.
