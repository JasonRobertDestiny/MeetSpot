"""用户相关SQLAlchemy模型与Pydantic模式。"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, String, func

from app.db.database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    phone = Column(String(20), unique=True, nullable=False)
    nickname = Column(String(50), nullable=False)
    avatar_url = Column(String(255), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))


class UserCreate(BaseModel):
    phone: str = Field(..., description="手机号")
    nickname: Optional[str] = Field(None, description="昵称，可选")
    avatar_url: Optional[str] = Field("", description="头像URL，可选")


class UserRead(BaseModel):
    id: str
    phone: str
    nickname: str
    avatar_url: str = ""
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

