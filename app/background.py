from datetime import datetime

from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import HelpRequest, RequestStatus


def timeout_overdue_requests() -> int:
    """Mark PENDING requests past their deadline as UNRESOLVED. Returns count."""
    session: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        q = (
            session.query(HelpRequest)
            .filter(HelpRequest.status == RequestStatus.PENDING)
            .filter(HelpRequest.timeout_deadline != None)
            .filter(HelpRequest.timeout_deadline < now)
        )
        count = 0
        for req in q.all():
            req.mark_unresolved()
            count += 1
        session.commit()
        return count
    finally:
        session.close()
