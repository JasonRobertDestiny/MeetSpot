import os
import threading
import tomllib
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = get_project_root()
WORKSPACE_ROOT = PROJECT_ROOT / "workspace"


class AMapSettings(BaseModel):
    """高德地图API配置"""
    api_key: str = Field(..., description="高德地图API密钥")
    security_js_code: Optional[str] = Field(None, description="高德地图JavaScript API安全密钥")


class LogSettings(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO", description="日志级别")
    file_path: str = Field(default="logs/meetspot.log", description="日志文件路径")


class AppConfig(BaseModel):
    """应用配置"""
    amap: AMapSettings = Field(..., description="高德地图API配置")
    log: Optional[LogSettings] = Field(default=LogSettings(), description="日志配置")

    class Config:
        arbitrary_types_allowed = True


class Config:
    """配置管理器（单例模式）"""
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._config = None
                    self._load_initial_config()
                    self._initialized = True

    def _load_initial_config(self):
        """加载初始配置"""
        try:
            # 首先尝试从环境变量加载（Vercel 部署）
            if os.getenv("AMAP_API_KEY"):
                self._config = AppConfig(
                    amap=AMapSettings(
                        api_key=os.getenv("AMAP_API_KEY", ""),
                        security_js_code=os.getenv("AMAP_SECURITY_JS_CODE", "")
                    )
                )
                return

            # 然后尝试从配置文件加载（本地开发）
            config_path = PROJECT_ROOT / "config" / "config.toml"
            if config_path.exists():
                with open(config_path, "rb") as f:
                    toml_data = tomllib.load(f)
                    
                amap_config = toml_data.get("amap", {})
                if not amap_config.get("api_key"):
                    raise ValueError("高德地图API密钥未配置")
                    
                self._config = AppConfig(
                    amap=AMapSettings(**amap_config),
                    log=LogSettings(**toml_data.get("log", {}))
                )
            else:
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
                
        except Exception as e:
            # 提供默认配置以防止启动失败
            print(f"配置加载失败，使用默认配置: {e}")
            self._config = AppConfig(
                amap=AMapSettings(
                    api_key=os.getenv("AMAP_API_KEY", ""),
                    security_js_code=os.getenv("AMAP_SECURITY_JS_CODE", "")
                )
            )

    def reload(self):
        """重新加载配置"""
        with self._lock:
            self._initialized = False
            self._load_initial_config()
            self._initialized = True

    @property
    def amap(self) -> AMapSettings:
        """获取高德地图配置"""
        return self._config.amap

    @property
    def log(self) -> LogSettings:
        """获取日志配置"""
        return self._config.log


# 全局配置实例
config = Config()
