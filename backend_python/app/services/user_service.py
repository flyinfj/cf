"""用户登录与注册，与 Java SystemUserServiceImpl 一致。"""
from sqlmodel import Session, select
from app.models.user import SystemUser
from app.schemas.user_schema import SystemUserCreate


def login(session: Session, user_name: str, password: str) -> SystemUser | None:
    user = session.exec(select(SystemUser).where(SystemUser.user_name == user_name)).first()
    if user and password == user.password:
        return user
    return None


def register(session: Session, user: SystemUserCreate) -> bool:
    if not user.userName or not user.password:
        return False
    existing = session.exec(select(SystemUser).where(SystemUser.user_name == user.userName)).first()
    if existing:
        return False
    new_user = SystemUser(user_name=user.userName, password=user.password)
    session.add(new_user)
    session.commit()
    return True
