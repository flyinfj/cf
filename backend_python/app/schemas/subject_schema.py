"""主题相关 schema（VO），与 Java entity.vo 一致；序列化为 camelCase 以适配前端。"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0].lower() + "".join(p.title() for p in parts[1:])


class SubjectDateVO(BaseModel):
    date: str


class SubjectInfoVO(BaseModel):
    """题材/行业股票信息。"""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    category1: Optional[str] = None
    category2: Optional[str] = None
    category3: Optional[str] = None
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    remarks: Optional[str] = None


class SubjectMessageDetailVO(BaseModel):
    """主题消息详情，含股票列表。"""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    create_time: Optional[datetime] = None
    category_code: Optional[str] = None
    category_name: Optional[str] = None
    pct_chg: Optional[float] = None
    description: Optional[str] = None
    stock_list: Optional[List[SubjectInfoVO]] = None


class IndustryCategoryVO(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    category_code: Optional[str] = None
    category: Optional[str] = None
