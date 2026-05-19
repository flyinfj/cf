"""健康检查 GET /health/check，与 Java HealthController 一致。"""
import time
from fastapi import APIRouter
from app.common import success

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/check")
def health_check():
    data = {
        "status": "ok",
        "message": "服务运行正常",
        "timestamp": str(int(time.time() * 1000)),
    }
    return success(data=data)
