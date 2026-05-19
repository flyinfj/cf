# 资讯后端服务（Python）

由原 Java Spring Boot 后端迁移，技术栈：**FastAPI + SQLModel**。接口路径与响应格式与前端兼容，无需改前端。

## 接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/ | 服务信息与可用接口 |
| GET | /api/health/check | 健康检查 |
| POST | /api/auth/login | 登录（body: userName, password） |
| POST | /api/auth/register | 注册（body: userName, password） |
| GET | /api/subject/dates | 主题日期列表 |
| GET | /api/subject/messages?date=YYYY-MM-DD | 按日期主题消息 |
| GET | /api/subject/industry/categories | 行业分类 |
| GET | /api/subject/messages/category?categoryCode= | 按分类主题消息 |
| GET | /api/subject/industry/stocks?categoryCode= | 行业股票列表 |

统一响应格式：`{ "code": 200, "message": "成功", "data": ... }`，错误时 `code` 为 500/404 等。

## 环境与运行

- Python 3.10+
- MySQL（与 Java 使用同一库 `cfdb`）

```bash
cd backend_python
pip install -r requirements.txt
# 可选：复制 .env.example 为 .env 并修改
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

服务启动后根路径为 `http://localhost:8080/api/`，与 Java 的 `context-path=/api` 一致。

## 配置

通过环境变量或 `.env` 覆盖默认值，参见 `app/config.py`。数据库连接与 Java `application.yml` 中保持一致即可。
