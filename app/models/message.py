"""聊天消息与投票记录模型。"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint, func

from app.db.database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


class VenueVote(Base):
    __tablename__ = "venue_votes"
    __table_args__ = (UniqueConstraint("room_id", "venue_id", "user_id", name="uq_vote"),)

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    room_id = Column(String(36), ForeignKey("gathering_rooms.id"), nullable=False)
    venue_id = Column(String(100), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    vote_type = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    room_id = Column(String(36), ForeignKey("gathering_rooms.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="聊天内容")


class VoteCreate(BaseModel):
    venue_id: str
    vote_type: str = Field(..., pattern="^(like|dislike)$")


class VoteRead(BaseModel):
    venue_id: str
    vote_type: str
    user_id: str
    created_at: Optional[datetime] = None

