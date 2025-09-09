from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import get_db
from .models import HelpRequest, KnowledgeItem, RequestStatus
from .schemas import HelpRequestOut, SupervisorAnswerIn

router = APIRouter(prefix="/supervisor", tags=["supervisor"])


@router.get("/pending", response_model=List[HelpRequestOut])
def list_pending(db: Session = Depends(get_db)):
	return (
		db.query(HelpRequest)
		.filter(HelpRequest.status == RequestStatus.PENDING)
		.order_by(HelpRequest.created_at.asc())
		.all()
	)


@router.get("/history", response_model=List[HelpRequestOut])
def list_history(db: Session = Depends(get_db)):
	return (
		db.query(HelpRequest)
		.filter(HelpRequest.status != RequestStatus.PENDING)
		.order_by(HelpRequest.updated_at.desc())
		.limit(200)
		.all()
	)


@router.post("/{request_id}/answer", response_model=HelpRequestOut)
def submit_answer(request_id: int, payload: SupervisorAnswerIn, db: Session = Depends(get_db)):
	help_req = db.get(HelpRequest, request_id)
	if not help_req:
		raise HTTPException(status_code=404, detail="Help request not found")
	if help_req.status != RequestStatus.PENDING:
		raise HTTPException(status_code=400, detail="Request already resolved or timed out")

	help_req.mark_resolved(payload.answer)
	db.add(help_req)
	# Update KB
	kb_item = KnowledgeItem(question=help_req.question, answer=payload.answer, source_request_id=help_req.id)
	db.add(kb_item)
	db.commit()
	db.refresh(help_req)

	print(f"[Agent->Caller {help_req.caller_id}] Thanks for waiting. Here's the answer: {payload.answer}")
	return help_req
