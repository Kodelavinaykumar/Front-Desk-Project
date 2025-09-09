# Frontdesk Human-in-the-Loop (Phase 1)

A minimal FastAPI app simulating an AI receptionist that escalates to a human supervisor, follows up with the caller, and learns new answers into a knowledge base.

## Stack
- FastAPI + Uvicorn
- SQLite via SQLAlchemy
- Minimal HTML/JS admin console

## Setup
1. Create and activate a venv (Windows PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Run the server:
   ```powershell
   uvicorn app.main:app --reload
   ```
3. Open `http://localhost:8000` for the Supervisor Console.
4. API docs: `http://localhost:8000/docs`.

## How it Works
- Agent endpoint `/agent/receive` simulates a phone call. It checks the knowledge base first; if found, it answers immediately and records a resolved trace. If unknown, it creates a PENDING `HelpRequest`, tells the caller it's checking with a supervisor, and logs a console message simulating a supervisor text.
- Supervisor console shows Pending, History, and Knowledge Base. Supervisors can submit an answer for a request; this both resolves the request and creates a `KnowledgeItem`. The agent then immediately "texts" the caller (console log) with the answer.
- A background worker marks overdue PENDING requests as UNRESOLVED after their `timeout_deadline`.

## Data Model
- `HelpRequest`: caller_id, question, status (PENDING/RESOLVED/UNRESOLVED), resolution, created/updated, timeout_deadline, resolved_at.
- `KnowledgeItem`: question, answer, created/updated, source_request_id.

## Simulating Calls
Use the docs or curl to simulate an inbound call:
```bash
curl -X POST http://localhost:8000/agent/receive -H "Content-Type: application/json" -d '{
  "caller_id": "+15551234567",
  "question": "What are your hours?",
  "timeout_seconds": 15
}'
```
If unknown, watch the server logs for the supervisor ping. Answer via the Supervisor Console or:
```bash
curl -X POST http://localhost:8000/supervisor/1/answer -H "Content-Type: application/json" -d '{"answer": "We are open 9am-6pm Mon-Sat."}'
```

## Design Notes
- Clear separation of concerns: routers for agent/supervisor/kb, background timeout worker, explicit models/schemas.
- Lifecycle enforced by status enum and timeout worker.
- KB writes capture provenance via `source_request_id`.
- Scales from 10→1000/day by swapping SQLite for Postgres, moving the timeout worker to a scheduler (e.g., Celery/APS, or Cloud scheduler), adding indexes, and placing the app behind a queue for burst handling. API contracts remain stable.

## Next Steps (Phase 2 hint)
- Live transfer if supervisor is available.
- Authentication/roles for supervisor console.
- Websocket push updates to console.
- Fuzzy KB retrieval with embeddings.
