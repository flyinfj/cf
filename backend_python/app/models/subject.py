"""主题相关表（仅用于类型/表名参考，复杂查询用原始 SQL）。"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class SubjectMessage(SQLModel, table=True):
    """表：subject_message。"""

    __tablename__ = "subject_message"

    create_time: Optional[datetime] = None
    category_code: Optional[str] = None
    category_name: Optional[str] = None
    pct_chg: Optional[float] = None
    description: Optional[str] = None


class SubjectInfo(SQLModel, table=True):
    """表：subject_info。"""

    __tablename__ = "subject_info"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_code: Optional[int] = None
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None


class SubjectRel(SQLModel, table=True):
    """表：subject_rel。"""

    __tablename__ = "subject_rel"

    category_code: Optional[str] = None
    par_category_code: Optional[str] = None
    category_type: Optional[str] = None
    category: Optional[str] = None
    par_category: Optional[str] = None
