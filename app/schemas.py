from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class HelpRequestCreate(BaseModel):
    caller_id: str
    question: str
    timeout_seconds: int = 900


class HelpRequestOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    caller_id: str
    question: str
    status: RequestStatus
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    timeout_deadline: Optional[datetime] = None

    class Config:
        from_attributes = True


class SupervisorAnswerIn(BaseModel):
    answer: str


class KnowledgeItemCreate(BaseModel):
    question: str
    answer: str
    source_request_id: Optional[int] = None


class KnowledgeItemOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    question: str
    answer: str
    source_request_id: Optional[int] = None

    class Config:
        from_attributes = True
