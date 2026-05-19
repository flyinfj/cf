# 资讯网站

一个基于React前端和Spring Boot后端的资讯网站。

## 技术栈

### 前端
- React 18.2.0
- React Router 6.16.0
- Ant Design 5.10.0
- Axios 1.5.1

### 后端
- Spring Boot 2.7.14
- Spring MVC
- MyBatis 2.3.1
- MySQL 8.0

## 项目结构

```
.
├── backend/                 # 后端项目
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/stock/
│   │   │   │   ├── controller/    # 控制器层
│   │   │   │   ├── service/       # 服务层
│   │   │   │   ├── dao/           # 数据访问层
│   │   │   │   ├── entity/        # 实体类
│   │   │   │   └── config/        # 配置类
│   │   │   └── resources/
│   │   │       ├── mapper/        # MyBatis映射文件
│   │   │       └── application.yml
│   │   └── pom.xml
│   └── README.md
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── utils/         # 工具类
│   │   └── App.js
│   ├── public/
│   └── package.json
└── README.md
```

## 功能特性

1. **用户认证**
   - 用户登录
   - 用户注册

2. **主页布局**
   - 顶部菜单栏
   - 左侧工作区（主题列表）
   - 右侧内容区（消息列表）

3. **热点信息**
   - 按日期显示主题列表
   - 显示当天的主题消息
   - 显示每条消息关联的列表

## 数据库表结构

### system_user（系统用户表）
- id: 主键ID
- user_name: 用户名
- password: 密码

### subject_message（题材消息表）
- create_time: 创建时间
- subject_id: 题材ID
- subject_name: 题材名称
- pct_chg: 涨幅百分比
- description: 描述内容

### subject_info（题材关联表）
- id: 主键ID
- subject_id: 题材ID
- stock_code: 代码
- stock_name: 名称

## 快速开始

### 后端启动

1. 确保已安装JDK 1.8+和Maven
2. 配置数据库连接（修改`backend/src/main/resources/application.yml`）
3. 执行数据库脚本（`backend/src/main/resources/db/schema.sql`）
4. 进入backend目录，运行：
```bash
mvn spring-boot:run
```

后端服务将在 http://localhost:8080 启动

### 前端启动

1. 确保已安装Node.js 16+
2. 进入frontend目录，安装依赖：
```bash
npm install
```
3. 启动开发服务器：
```bash
npm start
```

前端应用将在 http://localhost:3000 启动

## API接口

### 认证接口
- POST `/api/auth/login` - 用户登录
- POST `/api/auth/register` - 用户注册

### 主题接口
- GET `/api/subject/dates` - 获取主题日期列表
- GET `/api/subject/messages?date=YYYY-MM-DD` - 获取指定日期的消息列表

## 注意事项

1. 确保MySQL数据库已创建并配置正确
2. 前端请求地址配置在`frontend/src/utils/request.js`中
3. 后端跨域配置已启用，允许localhost:3000访问





