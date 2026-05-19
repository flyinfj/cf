"""认证接口：POST /auth/login, POST /auth/register，与 Java AuthController 一致。"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.common import success, error
from app.schemas.user_schema import SystemUserCreate, SystemUserResponse
from app.db import get_session
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(body: SystemUserCreate, session: Session = Depends(get_session)):
    user = user_service.login(session, body.userName or "", body.password or "")
    if user:
        return success(
            data=SystemUserResponse(id=user.id, user_name=user.user_name, password=None)
        )
    return error("用户名或密码错误")


@router.post("/register")
def register(body: SystemUserCreate, session: Session = Depends(get_session)):
    if not body.userName or not body.password:
        return error("用户名和密码不能为空")
    if user_service.register(session, body):
        return success(data="注册成功")
    return error("注册失败，用户名已存在")
