from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .db import get_db
from .models import KnowledgeItem
from .schemas import KnowledgeItemCreate, KnowledgeItemOut

router = APIRouter(prefix="/kb", tags=["kb"])


@router.get("/", response_model=List[KnowledgeItemOut])
def list_kb(db: Session = Depends(get_db)):
	return db.query(KnowledgeItem).order_by(KnowledgeItem.updated_at.desc()).all()


@router.post("/", response_model=KnowledgeItemOut)
def add_kb(item: KnowledgeItemCreate, db: Session = Depends(get_db)):
	entry = KnowledgeItem(
		question=item.question,
		answer=item.answer,
		source_request_id=item.source_request_id,
		search_text=f"{item.question}\n{item.answer}".strip(),
	)
	db.add(entry)
	db.commit()
	db.refresh(entry)
	return entry
