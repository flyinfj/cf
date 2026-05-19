"""全局异常处理，与 Java GlobalExceptionHandler 行为一致。"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.common.result import Result, error


# 404 时返回的可用接口说明（与 Java 一致）
NOT_FOUND_DATA = {
    "error": "未找到请求路径",
    "path": None,  # 由 handler 填充
    "message": "请确保路径以 /api 开头",
    "可用接口": {
        "健康检查": "GET /api/health/check",
        "用户登录": "POST /api/auth/login",
        "用户注册": "POST /api/auth/register",
        "获取主题日期": "GET /api/subject/dates",
        "获取主题消息": "GET /api/subject/messages?date=YYYY-MM-DD",
        "API信息": "GET /api/",
    },
}


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """404：未找到路径。"""
    NOT_FOUND_DATA["path"] = str(request.url.path)
    body = Result(code=404, message=f"未找到请求路径: {request.url.path}", data=NOT_FOUND_DATA)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=body.model_dump())


async def server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """500：服务器内部错误。"""
    msg = f"服务器内部错误: {exc!s}"
    body = error(msg, code=500)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body)
