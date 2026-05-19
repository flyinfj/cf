"""应用配置，与 Java application.yml 对齐。"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """从环境变量或 .env 读取配置。"""

    # 服务
    host: str = "0.0.0.0"
    port: int = 8080
    # 上下文路径在 FastAPI 中通过 prefix 实现，见 main.py

    # 数据库（与 Java 一致）
    db_driver: str = "mysql+pymysql"
    db_host: str = "120.27.198.74"
    db_port: int = 3306
    db_name: str = "cfdb"
    db_user: str = "cfuser"
    db_password: str = "Cf@123321"
    db_charset: str = "utf8"

    # CORS
    cors_enable_all_origins: bool = False
    cors_allowed_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:80,"
        "http://127.0.0.1:80,http://120.27.198.74:80,http://120.27.198.74,"
        "http://120.27.198.74:*,http://localhost:*,http://127.0.0.1:*"
    )

    @property
    def database_url(self) -> str:
        return (
            f"{self.db_driver}://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset={self.db_charset}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
