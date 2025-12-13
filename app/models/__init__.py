"""数据模型包。"""

from app.db.database import Base  # noqa: F401

# 导入所有模型以确保它们注册到Base.metadata
from app.models.user import User  # noqa: F401
from app.models.room import GatheringRoom, RoomParticipant  # noqa: F401
from app.models.message import ChatMessage, VenueVote  # noqa: F401

