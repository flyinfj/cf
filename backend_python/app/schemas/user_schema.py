"""用户相关请求/响应 DTO，与 Java SystemUser 一致。"""
from typing import Optional
from sqlmodel import SQLModel, Field


class SystemUserCreate(SQLModel):
    """登录/注册请求体：userName, password。"""

    userName: Optional[str] = None
    password: Optional[str] = None


class SystemUserResponse(SQLModel):
    """登录成功返回：不包含 password，字段名与 Java 一致（camelCase）。"""

    id: Optional[int] = None
    user_name: str = Field(serialization_alias="userName")
    password: Optional[str] = None  # 登录接口置空
