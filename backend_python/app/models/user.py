"""用户表，与 Java SystemUser 一致。请求/响应 DTO 见 app.schemas.user_schema。"""
from typing import Optional
from sqlmodel import SQLModel, Field


class SystemUser(SQLModel, table=True):
    """表：system_user。"""

    __tablename__ = "system_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    password: str
