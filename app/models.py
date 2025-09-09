from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db import Base


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class HelpRequest(Base):
    __tablename__ = "help_requests"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    caller_id = Column(String(64), nullable=False, index=True)
    question = Column(Text, nullable=False)
    status = Column(SAEnum(RequestStatus), default=RequestStatus.PENDING, nullable=False, index=True)
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    timeout_deadline = Column(DateTime, nullable=True)

    def mark_resolved(self, answer: str):
        self.status = RequestStatus.RESOLVED
        self.resolution = answer
        self.resolved_at = datetime.utcnow()

    def mark_unresolved(self):
        self.status = RequestStatus.UNRESOLVED
        self.resolved_at = datetime.utcnow()


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    question = Column(Text, nullable=False, index=True)
    answer = Column(Text, nullable=False)
    source_request_id = Column(Integer, ForeignKey("help_requests.id"), nullable=True)

    source_request = relationship("HelpRequest")
