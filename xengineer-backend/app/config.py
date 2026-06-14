"""XEngineer 配置管理模块

从 .env 文件读取环境变量，提供类型安全的配置访问。
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置，从 .env 文件和环境变量中加载"""

    # Agnes AI
    AGNES_API_Key: str = Field(default="", alias="AGNES_API_Key")

    # 火山引擎
    VOLCENGINE_APP_ID: str = Field(default="", alias="VOLCENGINE_APP_ID")
    VOLCENGINE_ACCESS_TOKEN: str = Field(default="", alias="VOLCENGINE_ACCESS_TOKEN")
    VOLCENGINE_SECRET_KEY: str = Field(default="", alias="VOLCENGINE_SECRET_KEY")

    # Pipeline 模式
    USE_REAL_NODES: bool = Field(default=False, alias="USE_REAL_NODES")

    model_config = {
        "env_file": str(Path(__file__).resolve().parents[2] / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# 全局配置单例
settings = Settings()