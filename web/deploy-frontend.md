
# 前端 Linux 部署指南（CentOS）

本文档说明如何将 React 前端应用部署到 CentOS 服务器上。

## 部署方式

有两种部署方式：

1.**使用 Nginx 部署静态文件**（推荐，生产环境）

2.**使用 Node.js 运行开发服务器**（仅用于测试）

## 方式一：使用 Nginx 部署（推荐）

### 前置要求

1. CentOS 7/8 服务器
2. Node.js 16+ 和 npm（用于构建）
3. Nginx（用于提供静态文件服务）
4. 具有 sudo 权限的用户

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
# CentOS/RHEL 7/8
sudo yum install nginx -y

# 如果使用 CentOS 8 或需要更新版本，可以添加 EPEL 仓库
sudo yum install epel-release -y
sudo yum install nginx -y

# 启动 Nginx 并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx
```

**配置 Nginx：**

在 CentOS 中，Nginx 配置文件位于 `/etc/nginx/conf.d/` 目录。创建或编辑配置文件 `/etc/nginx/conf.d/frontend.conf`：

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

```bash
# 测试配置
sudo nginx -t

# 如果测试通过，重启 Nginx
sudo systemctl restart nginx

# 检查 Nginx 状态
sudo systemctl status nginx
```

**注意：** CentOS 默认的 Nginx 配置可能包含默认站点配置，如果不需要可以删除或禁用：
```bash
# 备份默认配置
sudo mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak

# 或者编辑 /etc/nginx/nginx.conf，注释掉默认的 server 块
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

CentOS 默认使用 firewalld 防火墙：

```bash
# 允许 HTTP 流量
sudo firewall-cmd --permanent --add-service=http

# 允许 HTTPS 流量（如果配置了 HTTPS）
sudo firewall-cmd --permanent --add-service=https

# 重新加载防火墙配置
sudo firewall-cmd --reload

# 查看防火墙状态
sudo firewall-cmd --list-all
```

#### 6. 配置 SELinux（如需要）

如果 CentOS 启用了 SELinux，可能需要设置适当的上下文：

```bash
# 检查 SELinux 状态
getenforce

# 如果 SELinux 是 enforcing 模式，设置 Nginx 文件上下文
sudo chcon -Rt httpd_sys_content_t /var/www/html/frontend

# 或者临时允许 Nginx 访问（不推荐用于生产环境）
sudo setsebool -P httpd_can_network_connect 1
```

#### 7. 访问应用

在浏览器中访问：`http://your-server-ip` 或 `http://your-domain.com`

## 方式二：使用 Node.js 运行（仅测试用）

### 步骤

1.**在服务器上安装 Node.js**

```bash
# CentOS 使用 NodeSource 安装（推荐）
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 验证安装
node --version
npm --version

# 或使用 nvm（推荐用于多版本管理）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

2.**上传项目文件**

```bash

# 使用 Git 克隆

git clone your-repo-url

cd web/frontend

```

3.**安装依赖并启动**

```bash

npm install

npm start

```

4.**使用 PM2 管理进程（推荐）**

```bash

# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start npm --name "frontend" -- start

# 查看状态
pm2 status

# 查看日志
pm2 logs frontend

# 设置开机自启
pm2 startup
# 执行上面命令后，会输出一个命令，复制并执行它
pm2 save

```

## 配置 HTTPS（可选）

如果需要 HTTPS，可以使用 Let's Encrypt：

```bash
# CentOS 安装 Certbot
sudo yum install certbot python3-certbot-nginx -y

# 如果 yum 仓库中没有，可以使用 EPEL 仓库
sudo yum install epel-release -y
sudo yum install certbot python3-certbot-nginx -y

# 获取证书（替换为你的域名）
sudo certbot --nginx -d your-domain.com

# 测试自动续期
sudo certbot renew --dry-run

# 设置自动续期（certbot 会自动创建 systemd timer）
# 可以手动测试续期
sudo certbot renew
```

**注意：** 确保域名已正确解析到服务器 IP，并且防火墙已开放 80 和 443 端口。

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

检查 Nginx 配置中的 `root` 路径是否正确，以及文件权限：

```bash
# 检查文件权限
ls -la /var/www/html/frontend

# 设置正确的权限
sudo chown -R nginx:nginx /var/www/html/frontend
sudo chmod -R 755 /var/www/html/frontend

# 如果使用 SELinux，设置正确的上下文
sudo chcon -Rt httpd_sys_content_t /var/www/html/frontend
```

### 4. 构建文件过大

考虑使用代码分割和压缩优化：

- 检查 `package.json` 中的构建脚本
- 使用 `npm run build` 会自动进行优化

## 维护

### 更新部署

1. 在本地或构建服务器上重新构建
2. 上传新的 `build` 目录内容
3. 重新加载 Nginx 配置（通常不需要重启，但建议测试）

```bash
# 测试配置
sudo nginx -t

# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 或者重启 Nginx
sudo systemctl restart nginx
```

### 查看日志

```bash
# Nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# 查看 Nginx 服务状态
sudo systemctl status nginx

# 查看系统日志中的 Nginx 相关信息
sudo journalctl -u nginx -f
```

## CentOS 特定注意事项

### SELinux 配置

如果遇到权限问题，可能需要配置 SELinux：

```bash
# 检查 SELinux 状态
sestatus

# 临时禁用 SELinux（仅用于测试，不推荐生产环境）
sudo setenforce 0

# 永久禁用 SELinux（需要重启，不推荐）
sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
```

### 目录权限

确保 Nginx 可以访问静态文件：

```bash
# 设置目录所有者
sudo chown -R nginx:nginx /var/www/html/frontend

# 设置目录权限
sudo chmod -R 755 /var/www/html/frontend

# 如果使用 SELinux
sudo chcon -Rt httpd_sys_content_t /var/www/html/frontend
```

### 检查端口占用

```bash
# 检查 80 端口是否被占用
sudo netstat -tlnp | grep :80

# 或者使用 ss 命令
sudo ss -tlnp | grep :80
```

## 快速部署脚本

可以使用项目根目录下的 `deploy-frontend.sh` 脚本进行快速部署。确保脚本已针对 CentOS 进行配置。
