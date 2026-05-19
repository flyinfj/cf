"""数据库引擎与会话，供 SQLModel 使用。"""
from sqlmodel import Session, create_engine
from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


def get_session():
    """依赖注入：请求内使用同一 Session。"""
    with Session(engine) as session:
        yield session
