"""聚会房间相关的ORM与Pydantic模型。"""

import uuid
from datetime import datetime
from typing import Optional, Tuple

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, UniqueConstraint, func

from app.db.database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


class GatheringRoom(Base):
    __tablename__ = "gathering_rooms"

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    host_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    gathering_time = Column(DateTime(timezone=True))
    status = Column(String(20), default="pending")
    venue_keywords = Column(String(100), default="咖啡馆")
    final_venue_json = Column(Text, nullable=True)


class RoomParticipant(Base):
    __tablename__ = "room_participants"
    __table_args__ = (UniqueConstraint("room_id", "user_id", name="uq_room_user"),)

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    room_id = Column(String(36), ForeignKey("gathering_rooms.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    location_name = Column(String(200))
    location_lat = Column(Float)
    location_lng = Column(Float)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(String(20), default="member")


class GatheringRoomCreate(BaseModel):
    name: str = Field(..., description="聚会名称")
    description: str = Field("", description="聚会描述")
    gathering_time: Optional[datetime] = Field(
        None, description="聚会时间，ISO 字符串"
    )
    venue_keywords: str = Field("咖啡馆", description="场所类型关键词")


class RoomParticipantRead(BaseModel):
    user_id: str
    nickname: str
    location_name: Optional[str] = None
    location_coords: Optional[Tuple[float, float]] = None
    role: str

