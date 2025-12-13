"""常用数据库操作封装。"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


def _default_nickname(phone: str) -> str:
    suffix = phone[-4:] if len(phone) >= 4 else phone
    return f"用户{suffix}"


async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    """根据手机号查询用户。"""
    stmt = select(User).where(User.phone == phone)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """根据ID查询用户。"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, phone: str, nickname: Optional[str] = None, avatar_url: str = ""
) -> User:
    """创建新用户。"""
    user = User(
        phone=phone,
        nickname=nickname or _default_nickname(phone),
        avatar_url=avatar_url or "",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def touch_last_login(db: AsyncSession, user: User) -> None:
    """更新用户最近登录时间。"""
    user.last_login = datetime.utcnow()
    await db.commit()

