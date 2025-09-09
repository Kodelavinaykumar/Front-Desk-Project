from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .db import get_db
from .models import HelpRequest, KnowledgeItem, RequestStatus
from .schemas import HelpRequestCreate, HelpRequestOut

router = APIRouter(prefix="/agent", tags=["agent"])


FAKE_BUSINESS_PROMPT = (
    "You are the AI receptionist for 'Aurora Salon'. Business hours are 9am-6pm Mon-Sat. "
    "We offer haircuts ($40), coloring ($120+), and blowouts ($35). Location: 123 Main St."
)


def search_kb(db: Session, question: str) -> Optional[KnowledgeItem]:
    return (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.question.ilike(f"%{question.strip()}%"))
        .order_by(KnowledgeItem.updated_at.desc())
        .first()
    )


@router.post("/receive", response_model=HelpRequestOut)
def receive_call(payload: HelpRequestCreate, db: Session = Depends(get_db)):
    # Simulated LiveKit agent handling: try KB lookup first
    kb_hit = search_kb(db, payload.question)
    if kb_hit:
        print(f"[Agent] Answering caller {payload.caller_id} from KB: {kb_hit.answer}")
        # No help request needed; return a synthetic resolved object for traceability
        resolved = HelpRequest(
            caller_id=payload.caller_id,
            question=payload.question,
            status=RequestStatus.RESOLVED,
            resolution=kb_hit.answer,
            resolved_at=datetime.utcnow(),
        )
        db.add(resolved)
        db.commit()
        db.refresh(resolved)
        return resolved

    # Otherwise, create help request and notify supervisor (simulated)
    deadline = datetime.utcnow() + timedelta(seconds=int(payload.timeout_seconds))
    help_req = HelpRequest(
        caller_id=payload.caller_id,
        question=payload.question,
        status=RequestStatus.PENDING,
        timeout_deadline=deadline,
    )
    db.add(help_req)
    db.commit()
    db.refresh(help_req)

    print(
        f"[Agent] Caller {payload.caller_id}: 'Let me check with my supervisor and get back to you.'"
    )
    print(f"[Agent->Supervisor] Hey, I need help answering: {payload.question} (req #{help_req.id})")
    return help_req
