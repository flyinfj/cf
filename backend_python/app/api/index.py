"""根路径 GET /，与 Java IndexController 一致。"""
from fastapi import APIRouter
from app.common import success

router = APIRouter(tags=["index"])


@router.get("")
@router.get("/")
def index():
    data = {
        "name": "资讯后端服务",
        "version": "1.0.0",
        "status": "运行中",
        "可用接口": {
            "健康检查": "/api/health/check",
            "用户登录": "POST /api/auth/login",
            "用户注册": "POST /api/auth/register",
            "获取主题日期": "GET /api/subject/dates",
            "获取主题消息": "GET /api/subject/messages?date=YYYY-MM-DD",
        },
        "提示": "所有接口都需要以 /api 开头",
    }
    return success(data=data)
