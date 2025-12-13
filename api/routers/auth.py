"""认证相关API路由。"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token, get_current_user
from app.auth.sms import send_login_code, validate_code
from app.db import crud
from app.db.database import get_db
from app.models.user import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


class SendCodeRequest(BaseModel):
    phone: str = Field(..., min_length=4, max_length=20, description="手机号")


class VerifyCodeRequest(BaseModel):
    phone: str = Field(..., min_length=4, max_length=20, description="手机号")
    code: str = Field(..., min_length=4, max_length=10, description="验证码")
    nickname: str | None = Field(None, description="首次登录时的昵称")
    avatar_url: str | None = Field(None, description="头像URL，可选")


class AuthResponse(BaseModel):
    success: bool
    token: str
    user: dict


def _mask_phone(phone: str) -> str:
    """简单脱敏手机号。"""
    if len(phone) < 7:
        return phone
    return f"{phone[:3]}****{phone[-4:]}"


def _serialize_user(user: User) -> dict:
    """统一的用户返回结构。"""
    return {
        "id": user.id,
        "phone": _mask_phone(user.phone),
        "nickname": user.nickname,
        "avatar_url": user.avatar_url or "",
        "created_at": user.created_at,
        "last_login": user.last_login,
    }


@router.post("/send_code")
async def send_code(payload: SendCodeRequest):
    """下发登录验证码，MVP阶段固定返回Mock值。"""
    code = await send_login_code(payload.phone)
    return {"success": True, "message": "验证码已发送", "code": code}


@router.post("/verify_code", response_model=AuthResponse)
async def verify_code(
    payload: VerifyCodeRequest, db: AsyncSession = Depends(get_db)
):
    """验证验证码并返回JWT。"""
    if not validate_code(payload.phone, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误")

    user = await crud.get_user_by_phone(db, payload.phone)
    nickname = payload.nickname
    avatar_url = payload.avatar_url or ""

    # 首次登录创建用户；旧用户允许更新昵称
    if not user:
        user = await crud.create_user(db, phone=payload.phone, nickname=nickname, avatar_url=avatar_url)
    else:
        if nickname:
            user.nickname = nickname
            user.avatar_url = avatar_url or user.avatar_url
            await db.commit()
        await db.refresh(user)

    await crud.touch_last_login(db, user)

    token = create_access_token({"sub": user.id, "phone": user.phone})
    return {"success": True, "token": token, "user": _serialize_user(user)}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息。"""
    return {"user": _serialize_user(current_user)}

