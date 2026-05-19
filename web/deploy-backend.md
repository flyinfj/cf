# Linux 部署指南（CentOS 系统）

本文档针对 **CentOS** 系统编写，部署目录为 `/root/cf/web/backend`，使用 root 用户运行。

## 一、环境准备

### 1.1 检查 Java 环境

```bash

# 检查 Java 版本（需要 JDK 1.8 或更高版本）

java -version


# 如果没有安装 Java，使用以下命令安装

# CentOS/RHEL 系统（推荐）
sudo yum install java-1.8.0-openjdk java-1.8.0-openjdk-devel -y

# 或者 CentOS 8+ 使用 dnf
# sudo dnf install java-1.8.0-openjdk java-1.8.0-openjdk-devel -y


# Ubuntu/Debian 系统
# sudo apt update
# sudo apt install openjdk-8-jdk -y

```

### 1.2 检查 MySQL 连接

确保 Linux 服务器能够访问 MySQL 数据库（当前配置：120.27.198.74:3306）

```bash

# 测试数据库连接（如果 MySQL 客户端已安装）

mysql -h 120.27.198.74 -P 3306 -u cfuser -p

```

### 1.3 创建应用目录

```bash

# 创建应用目录（CentOS，root 用户）

mkdir -p /root/cf/web/backend

# 如果使用非 root 用户，需要设置权限
# sudo mkdir -p /root/cf/web/backend
# sudo chown your-username:your-group /root/cf/web/backend

```

## 二、文件传输

### 2.1 使用 SCP 传输文件

在 Windows 机器上执行（PowerShell 或 CMD）：

```powershell

# 将 JAR 文件传输到 Linux 服务器

scp backend/target/stock-info-backend-1.0.0.jar user@your-linux-server:/root/cf/web/backend/

```

### 2.2 使用 FTP/SFTP 工具

使用 FileZilla、WinSCP 等工具将 `stock-info-backend-1.0.0.jar` 上传到 Linux 服务器。

### 2.3 直接下载（如果 JAR 在版本控制或文件服务器上）

```bash

# 在 Linux 服务器上执行

cd /root/cf/web/backend

wget http://your-file-server/stock-info-backend-1.0.0.jar

```

## 三、配置文件管理

### 3.1 创建外部配置文件（推荐）

在应用目录创建 `application.yml` 或 `application.properties`，这样可以不修改 JAR 包：

```bash

cd /root/cf/web/backend

vim application.yml

```

配置文件内容：

```yaml

server:

  port: 8080

  servlet:

    context-path: /api


spring:

  mvc:

    throw-exception-if-no-handler-found: true

  web:

    resources:

      add-mappings: false

  datasource:

    driver-class-name: com.mysql.cj.jdbc.Driver

    url: jdbc:mysql://120.27.198.74:3306/cfdb?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai

    username: cfuser

    password: Cf@123321


mybatis:

  mapper-locations: classpath:mapper/*.xml

  type-aliases-package: com.stock.entity

  configuration:

    map-underscore-to-camel-case: true

    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl


logging:

  level:

    com.stock: debug

    org.springframework.web: info

  file:

    name: /root/cf/web/backend/logs/application.log

  pattern:

    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"

```

### 3.2 创建日志目录

```bash

mkdir -p /root/cf/web/backend/logs

```

## 四、启动应用

### 4.1 简单启动（前台运行，用于测试）

```bash

cd /root/cf/web/backend

java -jar stock-info-backend-1.0.0.jar

```

### 4.2 后台启动（使用 nohup）

```bash

cd /root/cf/web/backend

nohup java -jar stock-info-backend-1.0.0.jar > logs/console.log 2>&1 &

echo $! > app.pid  # 保存进程 ID

```

### 4.3 使用外部配置文件启动

```bash

cd /root/cf/web/backend

java -jar stock-info-backend-1.0.0.jar --spring.config.location=file:./application.yml

```

### 4.4 设置 JVM 参数启动（推荐生产环境）

```bash

cd /root/cf/web/backend

nohup java -Xms256m -Xmx512m -XX:+UseG1GC \

  -jar stock-info-backend-1.0.0.jar \

  --spring.config.location=file:./application.yml \

  > logs/console.log 2>&1 &

echo $! > app.pid

```

参数说明：

-`-Xms256m`: 初始堆内存 256MB

-`-Xmx512m`: 最大堆内存 512MB

-`-XX:+UseG1GC`: 使用 G1 垃圾回收器

## 五、创建启动脚本

### 5.1 创建启动脚本 `start.sh`

```bash

cd /root/cf/web/backend

vim start.sh

```

脚本内容：

```bash

#!/bin/bash


APP_NAME="stock-info-backend"

APP_JAR="stock-info-backend-1.0.0.jar"

APP_DIR="/root/cf/web/backend"

LOG_DIR="$APP_DIR/logs"

PID_FILE="$APP_DIR/app.pid"


# 进入应用目录

cd $APP_DIR


# 检查 JAR 文件是否存在

if [ ! -f "$APP_JAR" ]; then

    echo "错误: $APP_JAR 文件不存在!"

    exit 1

fi


# 检查是否已经运行

if [ -f "$PID_FILE" ]; then

    PID=$(cat $PID_FILE)

    if ps -p $PID > /dev/null 2>&1; then

        echo "应用已经在运行中 (PID: $PID)"

        exit 1

    else

        rm -f $PID_FILE

    fi

fi


# 创建日志目录

mkdir -p $LOG_DIR


# 启动应用

echo "正在启动 $APP_NAME..."

nohup java -Xms256m -Xmx512m -XX:+UseG1GC \

  -jar $APP_JAR \

  --spring.config.location=file:./application.yml \

  > $LOG_DIR/console.log 2>&1 &


# 保存进程 ID

echo $! > $PID_FILE


# 等待几秒检查启动状态

sleep 3

if ps -p $(cat $PID_FILE) > /dev/null 2>&1; then

    echo "$APP_NAME 启动成功 (PID: $(cat $PID_FILE))"

    echo "日志文件: $LOG_DIR/console.log"

else

    echo "$APP_NAME 启动失败，请查看日志: $LOG_DIR/console.log"

    rm -f $PID_FILE

    exit 1

fi

```

### 5.2 创建停止脚本 `stop.sh`

```bash

cd /root/cf/web/backend

vim stop.sh

```

脚本内容：

```bash

#!/bin/bash


APP_NAME="stock-info-backend"

APP_DIR="/root/cf/web/backend"

PID_FILE="$APP_DIR/app.pid"


if [ ! -f "$PID_FILE" ]; then

    echo "$APP_NAME 未运行"

    exit 1

fi


PID=$(cat $PID_FILE)


if ! ps -p $PID > /dev/null 2>&1; then

    echo "$APP_NAME 未运行"

    rm -f $PID_FILE

    exit 1

fi


echo "正在停止 $APP_NAME (PID: $PID)..."

kill $PID


# 等待进程结束

for i in {1..30}; do

    if ! ps -p $PID > /dev/null 2>&1; then

        echo "$APP_NAME 已停止"

        rm -f $PID_FILE

        exit 0

    fi

    sleep 1

done


# 如果还在运行，强制杀死

if ps -p $PID > /dev/null 2>&1; then

    echo "强制停止 $APP_NAME..."

    kill -9 $PID

    rm -f $PID_FILE

    echo "$APP_NAME 已强制停止"

fi

```

### 5.3 创建重启脚本 `restart.sh`

```bash

cd /root/cf/web/backend

vim restart.sh

```

脚本内容：

```bash

#!/bin/bash


APP_DIR="/root/cf/web/backend"


cd $APP_DIR

./stop.sh

sleep 2

./start.sh

```

### 5.4 设置脚本执行权限

```bash

cd /root/cf/web/backend

chmod +x start.sh stop.sh restart.sh

```

## 六、使用 Systemd 管理服务（推荐生产环境）

### 6.1 创建 systemd 服务文件

```bash

sudo vim /etc/systemd/system/stock-info-backend.service

```

服务文件内容：

```ini

[Unit]

Description=Stock Info Backend Service

After=network.target mysql.service


[Service]

Type=simple

User=root

Group=root

WorkingDirectory=/root/cf/web/backend

ExecStart=/usr/bin/java -Xms256m -Xmx512m -XX:+UseG1GC -jar /root/cf/web/backend/stock-info-backend-1.0.0.jar --spring.config.location=file:/root/cf/web/backend/application.yml

ExecStop=/bin/kill -15 $MAINPID

Restart=always

RestartSec=10

StandardOutput=append:/root/cf/web/backend/logs/console.log

StandardError=append:/root/cf/web/backend/logs/error.log


[Install]

WantedBy=multi-user.target

```

**注意**: 当前配置使用 root 用户运行。如果使用非 root 用户，请将 `User=root` 和 `Group=root` 替换为实际的用户名和组名。

### 6.2 使用 systemd 管理服务

```bash

# 重新加载 systemd 配置

sudo systemctl daemon-reload


# 启动服务

sudo systemctl start stock-info-backend


# 停止服务

sudo systemctl stop stock-info-backend


# 重启服务

sudo systemctl restart stock-info-backend


# 查看服务状态

sudo systemctl status stock-info-backend


# 设置开机自启

sudo systemctl enable stock-info-backend


# 取消开机自启

sudo systemctl disable stock-info-backend


# 查看日志

sudo journalctl -u stock-info-backend -f

```

## 七、验证部署

### 7.1 检查服务是否启动

```bash

# 检查进程

ps aux | grep stock-info-backend


# 检查端口

netstat -tlnp | grep 8080

# 或使用 ss 命令

ss -tlnp | grep 8080


# 检查服务状态（如果使用 systemd）

sudo systemctl status stock-info-backend

```

### 7.2 测试 API 接口

```bash

# 健康检查

curl http://localhost:8080/api/health


# 或使用浏览器访问

# http://your-server-ip:8080/api/health

```

## 八、防火墙配置

如果 Linux 服务器开启了防火墙，需要开放 8080 端口：

```bash

# CentOS/RHEL 7+ (firewalld) - 推荐
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload

# 或者临时开放（重启后失效）
# sudo firewall-cmd --add-port=8080/tcp


# CentOS/RHEL 6 (iptables)
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo service iptables save

# 或者 CentOS 7 使用 iptables（如果禁用了 firewalld）
# sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
# sudo service iptables save


# Ubuntu/Debian (ufw)
# sudo ufw allow 8080/tcp
# sudo ufw reload

```

## 九、日志管理

### 9.1 查看日志

```bash

# 查看控制台日志

tail -f /root/cf/web/backend/logs/console.log


# 查看应用日志（如果配置了文件日志）

tail -f /root/cf/web/backend/logs/application.log


# 查看 systemd 日志

sudo journalctl -u stock-info-backend -f

```

### 9.2 日志轮转（可选）

创建 logrotate 配置：

```bash

sudo vim /etc/logrotate.d/stock-info-backend

```

配置内容：

```

/root/cf/web/backend/logs/*.log {

    daily

    rotate 7

    compress

    delaycompress

    missingok

    notifempty

    create 0644 root root

}

```

## 十、常见问题排查

### 10.1 端口被占用

```bash

# 查找占用 8080 端口的进程

lsof -i:8080

# 或

netstat -tlnp | grep 8080


# 杀死进程

kill -9 <PID>

```

### 10.2 数据库连接失败

- 检查数据库服务器是否可访问：`ping 120.27.198.74`
- 检查防火墙是否允许数据库端口（3306）
- 检查数据库用户名和密码是否正确
- 检查数据库是否已创建（cfdb）

### 10.3 Java 版本不兼容

```bash

# 检查 Java 版本

java -version


# 如果版本不对，设置 JAVA_HOME

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

export PATH=$JAVA_HOME/bin:$PATH

```

### 10.4 内存不足

如果服务器内存较小，可以调整 JVM 参数：

```bash

# 修改启动脚本中的内存参数

-Xms256m -Xmx512m  # 根据实际情况调整

```

### 10.5 权限问题

```bash

# 确保应用目录有读写权限（CentOS，root 用户）
# 如果是 root 用户，通常不需要修改权限
# 如果使用非 root 用户，需要设置权限：
# sudo chown -R your-username:your-group /root/cf/web/backend

chmod +x /root/cf/web/backend/*.sh

```

## 十一、快速部署检查清单

- [ ] Java 1.8+ 已安装
- [ ] JAR 文件已上传到服务器
- [ ] 应用目录已创建（/root/cf/web/backend）
- [ ] 外部配置文件已创建（application.yml）
- [ ] 日志目录已创建
- [ ] 启动/停止脚本已创建并设置执行权限
- [ ] 防火墙端口已开放（8080）
- [ ] 数据库连接正常
- [ ] 服务已启动并验证
- [ ] （可选）systemd 服务已配置
- [ ] （可选）开机自启已设置

## 十二、更新部署

当需要更新应用时：

```bash

# 1. 停止当前服务

cd /root/cf/web/backend

./stop.sh

# 或

sudo systemctl stop stock-info-backend


# 2. 备份旧版本（可选）

cp stock-info-backend-1.0.0.jarstock-info-backend-1.0.0.jar.bak


# 3. 上传新版本 JAR 文件


# 4. 启动服务

./start.sh

# 或

sudo systemctl start stock-info-backend


# 5. 验证服务

curl http://localhost:8080/api/health

```

---

**部署完成后，应用将在 `http://your-server-ip:8080/api` 提供服务。**
