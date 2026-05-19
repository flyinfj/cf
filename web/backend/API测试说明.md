# API访问说明

## 服务地址

**基础URL**: `http://localhost:8080/api`

注意：`/api` 是上下文路径（context-path），不是具体的接口地址。

## 正确的接口地址

### 1. 用户认证接口

#### 登录接口
- **URL**: `http://localhost:8080/api/auth/login`
- **方法**: POST
- **请求体**:
```json
{
  "userName": "test",
  "password": "123456"
}
```

#### 注册接口
- **URL**: `http://localhost:8080/api/auth/register`
- **方法**: POST
- **请求体**:
```json
{
  "userName": "test",
  "password": "123456"
}
```

### 2. 主题信息接口

#### 获取主题日期列表
- **URL**: `http://localhost:8080/api/subject/dates`
- **方法**: GET
- **响应示例**:
```json
{
  "code": 200,
  "message": "成功",
  "data": [
    {"date": "2024-12-09"},
    {"date": "2024-12-08"}
  ]
}
```

#### 获取指定日期的消息列表
- **URL**: `http://localhost:8080/api/subject/messages?date=2024-12-09`
- **方法**: GET
- **参数**: date (格式: YYYY-MM-DD)

## 测试方法

### 使用浏览器测试GET接口
直接在浏览器访问：
```
http://localhost:8080/api/subject/dates
```

### 使用curl测试POST接口
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"userName\":\"test\",\"password\":\"123456\"}"
```

### 使用Postman测试
1. 创建新请求
2. 选择方法（GET/POST）
3. 输入完整URL（包含/api前缀）
4. 如果是POST，在Body中选择raw JSON，输入JSON数据

## 常见问题

### 1. 访问 http://localhost:8080/api 返回404
**原因**: `/api` 只是上下文路径，不是实际接口
**解决**: 访问具体的接口地址，如 `http://localhost:8080/api/subject/dates`

### 2. 服务启动失败
**检查**:
- 数据库连接是否正常
- 端口8080是否被占用
- 查看控制台错误日志

### 3. 数据库连接失败
**检查**:
- `application.yml` 中的数据库配置
- 数据库服务是否运行
- 网络连接是否正常

## 服务状态检查

### 检查端口是否监听
```bash
netstat -ano | findstr :8080
```

### 检查服务日志
查看控制台输出的Spring Boot启动日志，确认服务是否成功启动。




