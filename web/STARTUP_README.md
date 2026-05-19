# 股票资讯系统启动指南

## 项目结构
```
web/
├── backend/          # Spring Boot后端
├── frontend/         # React前端
└── scripts/          # 启动脚本
```

## 快速启动

### 方法一：使用主启动脚本（推荐）
双击运行 `start-project.bat`，选择启动选项：
- [1] 只启动前端
- [2] 只启动后端
- [3] 同时启动前后端
- [4] 退出

### 方法二：分别启动

#### 启动后端
- 批处理：双击 `start-backend.bat`
- PowerShell：运行 `.\start-backend.ps1`
- 手动：`cd backend && mvn spring-boot:run`

#### 启动前端
- 批处理：双击 `start-frontend.bat`
- PowerShell：运行 `.\start-frontend.ps1`
- 手动：`cd frontend && npm start`

## 服务地址
- 前端：http://localhost:3000
- 后端：http://localhost:8080

## 注意事项
1. 首次运行前端时会自动安装依赖包，请耐心等待
2. 后端需要Java 8+和Maven环境
3. 前端需要Node.js环境
4. 如果端口被占用，脚本会提示选择其他端口

## 数据库配置
确保在 `backend/src/main/resources/application.yml` 中正确配置数据库连接信息。

## 常见问题
1. 如果遇到端口占用，请修改配置文件中的端口号
2. 如果前端启动失败，尝试删除 `frontend/node_modules` 重新安装
3. 确保防火墙允许相关端口的访问
