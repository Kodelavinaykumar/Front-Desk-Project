from threading import Thread, Event
from time import sleep

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

# Static (CSS/JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})


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
