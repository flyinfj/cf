"""FastAPI 应用入口，与 Java context-path /api、CORS、全局异常一致。"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.common import Result, error
from app.exceptions import NOT_FOUND_DATA, not_found_handler, server_error_handler
from app.api import auth, index, health, subject

app = FastAPI(
    title="资讯后端服务",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

# 统一前缀 /api（与 Java server.servlet.context-path 一致）
app.include_router(auth.router, prefix="/api")
app.include_router(index.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(subject.router, prefix="/api")


# CORS（与 Java WebConfig 一致）
def _get_origins():
    if settings.cors_enable_all_origins:
        return ["*"]
    return [o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()]


app.add_middleware(
    "CORSMiddleware",
    allow_origins=_get_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    max_age=3600,
)


# 404：未找到路径（与 Java GlobalExceptionHandler 一致）
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        data = {**NOT_FOUND_DATA, "path": request.url.path}
        body = Result(code=404, message=f"未找到请求路径: {request.url.path}", data=data)
        return JSONResponse(status_code=404, content=body.model_dump())
    return JSONResponse(
        status_code=exc.status_code,
        content=error(exc.detail or "错误", code=exc.status_code),
    )


# 500：服务器内部错误
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return await server_error_handler(request, exc)


# 请求体验证错误时仍返回 Result 格式
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    msg = "请求参数错误: " + str(exc.errors())
    return JSONResponse(
        status_code=422,
        content=error(msg, code=422),
    )
