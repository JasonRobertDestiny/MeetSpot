"""数据库引擎与会话管理。

使用SQLite作为MVP默认存储，保留通过环境变量`DATABASE_URL`切换到PostgreSQL的能力。
"""

import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base


# 项目根目录，默认将SQLite数据库放在data目录下
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# 允许通过环境变量覆盖数据库连接串
DEFAULT_SQLITE_PATH = DATA_DIR / "meetspot.db"
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite+aiosqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"
)

# 创建异步引擎与会话工厂
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

# 统一的ORM基类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供数据库会话并确保正确关闭。"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """在启动时创建数据库表。"""
    # 延迟导入以避免循环依赖
    from app import models  # noqa: F401  确保所有模型已注册

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

