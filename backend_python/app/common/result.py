"""统一 API 响应体，与 Java Result<T> 一致；序列化时使用 by_alias 以适配前端 camelCase。"""
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


def _serialize(data: Any) -> Any:
    """递归序列化，对 Pydantic 模型使用 model_dump(by_alias=True)。"""
    if hasattr(data, "model_dump"):
        return data.model_dump(by_alias=True)
    if isinstance(data, list):
        return [_serialize(x) for x in data]
    if isinstance(data, dict):
        return {k: _serialize(v) for k, v in data.items()}
    return data


class Result(BaseModel, Generic[T]):
    """code=200 成功，500/404 错误；message 提示；data 为业务数据。"""

    code: int
    message: str
    data: Optional[T] = None


def success(data: T = None, message: str = "成功") -> dict:
    """返回可直接 JSON 序列化的 dict，嵌套模型按 alias（camelCase）输出。"""
    return {"code": 200, "message": message, "data": _serialize(data)}


def error(message: str, code: int = 500) -> dict:
    """返回错误体 dict。"""
    return {"code": code, "message": message, "data": None}
