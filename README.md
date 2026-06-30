# AI Career Copilot

AI-powered SaaS platform for student placement readiness, resume intelligence, job matching, skill gaps, roadmaps, RAG career assistance, and mock interviews.

## Local Setup

1. Copy `.env.example` to `.env`.
2. Fill `JWT_SECRET_KEY` and `GEMINI_API_KEY`.
3. Install backend dependencies with uv:

```bash
cd backend
uv sync
```

4. Start the stack:

```bash
docker compose up --build
```

5. Run migrations:

```bash
docker compose exec backend uv run alembic upgrade head
```

For local backend-only development:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Services:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- ChromaDB: `http://localhost:8001`
