# QueryFlow AI

QueryFlow AI is a RAG-based AI agent that allows you to interact with your SQL databases using Natural Language. It securely connects to your database, understands the schema, and generates safe, read-only SQL queries to answer your questions.

## 🚀 Quick Start

### Prerequisites

1. **PostgreSQL**: Ensure you have a Postgres database running.
    * Default URL: `postgresql://postgres:postgres@localhost:5432/queryflow`
    * The app will automatically create tables in this database.
2. **Ollama** (for local LLM):
    * Install from [ollama.com](https://ollama.com).
    * Run `ollama serve`.
    * Pull a model: `ollama pull llama3` (or update `.env` with your preferred model).
3. **Node.js** (v18+) and **Python** (v3.10+).

### Installation

1. **Backend Setup**:

    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Initialize Database
    alembic init alembic # (Already done in repo)
    alembic revision --autogenerate -m "Initial schema"
    alembic upgrade head
    ```

2. **Frontend Setup**:

    ```bash
    cd frontend
    npm install
    ```

### 🏃‍♂️ Running the Project

We have a convenience script that runs both Backend (FastAPI) and Frontend (Next.js) in parallel:

```bash
# From the root directory
./start_dev.sh
```

* **Backend**: Runs on `http://localhost:8000`
* **Frontend**: Runs on `http://localhost:3000`
* **API Docs**: `http://localhost:8000/docs`

### 💡 How to Use

1. **Login**: Open `http://localhost:3000`. Use any username/password (currently in dev mode, it will auto-register).
2. **Dashboard**: You will see a list of Database Connections.
    * *Note*: In Phase 1, a default "Production DB" connection is stubbed.
3. **Ingest Schema**:
    * Click the **Ingest** button on the connection card.
    * This triggers the AI to inspect your database tables and learn the schema.
4. **Query**:
    * Click **Query**.
    * Type a question in English, e.g., *"Show me the top 10 users by created date"*.
    * Click **Run AI**.
    * The system will generate the SQL, execute it (read-only), and show results.

## 🏗 Architecture

* **Backend**: FastAPI, SQLAlchemy, LangGraph (AI Pipeline), ChromaDB (Vector Store).
* **Frontend**: Next.js 14, TailwindCSS, Shadcn UI.
* **AI Pipeline**:
  * **Intent Classifier**: Decides if request is Read or Write.
  * **Retriever**: Finds relevant table schemas.
  * **Generator**: Creates SQL queries.
  * **Guardrails**: Ensures queries are strictly `SELECT` only.
