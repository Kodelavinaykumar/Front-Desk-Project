from threading import Thread, Event
from time import sleep

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .db import Base, engine
from .background import timeout_overdue_requests
from .routers_agent import router as agent_router
from .routers_supervisor import router as supervisor_router
from .routers_kb import router as kb_router

app = FastAPI(title="Frontdesk Human-in-the-Loop")

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(agent_router)
app.include_router(supervisor_router)
app.include_router(kb_router)

# Static (not used heavily but available)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Supervisor Console</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 24px; }
                section { margin-bottom: 24px; }
                button { padding: 6px 10px; }
                input, textarea { width: 320px; }
            </style>
        </head>
        <body>
            <h2>Supervisor Console</h2>
            <section>
                <h3>Pending Requests</h3>
                <div id="pending"></div>
            </section>
            <section>
                <h3>History</h3>
                <div id="history"></div>
            </section>
            <section>
                <h3>Knowledge Base</h3>
                <div>
                    <input id="kb_q" placeholder="Question"/> <br/>
                    <textarea id="kb_a" placeholder="Answer"></textarea><br/>
                    <button onclick="addKb()">Add KB Item</button>
                </div>
                <div id="kb"></div>
            </section>
            <script>
                async function fetchPending() {
                    const r = await fetch('/supervisor/pending');
                    const items = await r.json();
                    document.getElementById('pending').innerHTML = items.map(i => `
                        <div style="margin-bottom:12px;">
                            <div><b>#${i.id}</b> [${i.status}] <b>${i.caller_id}</b>: ${i.question}</div>
                            <input id="ans_${i.id}" placeholder="Answer..."/>
                            <button onclick="answer(${i.id})">Submit</button>
                        </div>
                    `).join('');
                }
                async function fetchHistory() {
                    const r = await fetch('/supervisor/history');
                    const items = await r.json();
                    document.getElementById('history').innerHTML = items.map(i => `
                        <div style="margin-bottom:6px;">#${i.id} [${i.status}] ${i.caller_id} → ${i.resolution || ''}</div>
                    `).join('');
                }
                async function fetchKb() {
                    const r = await fetch('/kb/');
                    const items = await r.json();
                    document.getElementById('kb').innerHTML = items.map(k => `
                        <div style="margin-bottom:6px;"><b>Q</b>: ${k.question} <br/> <b>A</b>: ${k.answer}</div>
                    `).join('');
                }
                async function answer(id) {
                    const val = (document.getElementById('ans_' + id) || {}).value || '';
                    if (!val) return alert('Provide an answer');
                    await fetch(`/supervisor/${id}/answer`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ answer: val }) });
                    fetchPending(); fetchHistory(); fetchKb();
                }
                async function addKb() {
                    const q = document.getElementById('kb_q').value || '';
                    const a = document.getElementById('kb_a').value || '';
                    if (!q || !a) return alert('Enter both question and answer');
                    await fetch('/kb/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: q, answer: a }) });
                    document.getElementById('kb_q').value = ''; document.getElementById('kb_a').value='';
                    fetchKb();
                }
                function loop() { fetchPending(); fetchHistory(); fetchKb(); setTimeout(loop, 3000); }
                loop();
            </script>
        </body>
        </html>
        """
    )


# Background thread to timeout overdue requests
_stop_event = Event()

def _timeout_worker():
    while not _stop_event.is_set():
        count = timeout_overdue_requests()
        if count:
            print(f"[Timeout] Marked {count} request(s) as UNRESOLVED")
        sleep(5)


worker = Thread(target=_timeout_worker, daemon=True)
worker.start()
