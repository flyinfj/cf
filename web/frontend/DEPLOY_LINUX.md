# 前端 Linux 部署指南

本文档说明如何将 React 前端应用部署到 Linux 服务器上。

## 部署方式

有两种部署方式：
1. **使用 Nginx 部署静态文件**（推荐，生产环境）
2. **使用 Node.js 运行开发服务器**（仅用于测试）

## 方式一：使用 Nginx 部署（推荐）

### 前置要求

1. Linux 服务器（Ubuntu/CentOS 等）
2. Node.js 16+ 和 npm（用于构建）
3. Nginx（用于提供静态文件服务）

### 步骤

#### 1. 在本地或构建服务器上构建项目

```bash
cd frontend
npm install
npm run build
```

构建完成后，会在 `frontend/build` 目录下生成静态文件。

#### 2. 将构建文件上传到 Linux 服务器

可以使用以下方式之一：

**方式 A：使用 SCP**
```bash
scp -r frontend/build/* user@your-server:/var/www/html/frontend/
```

**方式 B：使用 SFTP 工具**
- 使用 FileZilla、WinSCP 等工具上传 `frontend/build` 目录下的所有文件

**方式 C：使用 Git**
```bash
# 在服务器上克隆项目
git clone your-repo-url
cd web/frontend
npm install
npm run build
```

#### 3. 安装和配置 Nginx

**安装 Nginx：**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx -y

# CentOS/RHEL
sudo yum install nginx -y
```

**配置 Nginx：**

创建或编辑配置文件 `/etc/nginx/sites-available/frontend`（Ubuntu）或 `/etc/nginx/conf.d/frontend.conf`（CentOS）：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或 IP

    root /var/www/html/frontend;
    index index.html;

    # 处理 React Router 的路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
```

**启用配置：**

Ubuntu:
```bash
sudo ln -s /etc/nginx/sites-available/frontend /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

CentOS:
```bash
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

#### 4. 配置后端 API 地址

在部署前，需要修改 `frontend/src/utils/request.js` 中的 API 地址：

```javascript
const request = axios.create({
  baseURL: 'http://your-backend-server:8080/api',  // 替换为实际的后端地址
  timeout: 10000,
});
```

然后重新构建：
```bash
npm run build
```

**或者使用环境变量（推荐）：**

修改 `frontend/src/utils/request.js`：
```javascript
const request = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8080/api',
  timeout: 10000,
});
```

构建时指定环境变量：
```bash
REACT_APP_API_URL=http://your-backend-server:8080/api npm run build
```

#### 5. 设置防火墙（如需要）

```bash
# Ubuntu (UFW)
sudo ufw allow 'Nginx Full'

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

#### 6. 访问应用

在浏览器中访问：`http://your-server-ip` 或 `http://your-domain.com`

## 方式二：使用 Node.js 运行（仅测试用）

### 步骤

1. **在服务器上安装 Node.js**
```bash
# 使用 NodeSource 安装（推荐）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 或使用 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

2. **上传项目文件**
```bash
# 使用 Git 克隆
git clone your-repo-url
cd web/frontend
```

3. **安装依赖并启动**
```bash
npm install
npm start
```

4. **使用 PM2 管理进程（推荐）**
```bash
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start npm --name "frontend" -- start

# 查看状态
pm2 status

# 设置开机自启
pm2 startup
pm2 save
```

## 配置 HTTPS（可选）

如果需要 HTTPS，可以使用 Let's Encrypt：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 常见问题

### 1. 路由刷新 404 错误

确保 Nginx 配置中包含：
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 2. API 请求跨域问题

在后端配置 CORS，允许前端域名访问。

### 3. 静态资源加载失败

检查 Nginx 配置中的 `root` 路径是否正确，以及文件权限。

### 4. 构建文件过大

考虑使用代码分割和压缩优化：
- 检查 `package.json` 中的构建脚本
- 使用 `npm run build` 会自动进行优化

## 维护

### 更新部署

1. 在本地或构建服务器上重新构建
2. 上传新的 `build` 目录内容
3. 重启 Nginx（通常不需要，但建议测试）

```bash
sudo systemctl reload nginx
```

### 查看日志

```bash
# Nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# Nginx 访问日志
sudo tail -f /var/log/nginx/access.log
```

## 快速部署脚本

可以使用项目根目录下的 `deploy-frontend.sh` 脚本进行快速部署。

