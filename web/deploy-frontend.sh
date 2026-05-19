#!/bin/bash

# 前端 Linux 部署脚本
# 使用方法: ./deploy-frontend.sh [选项]
# 选项:
#   --build-only    仅构建，不上传
#   --upload-only   仅上传，不构建（需要先有 build 目录）
#   --server=IP     指定服务器 IP
#   --user=USER     指定 SSH 用户
#   --path=PATH     指定服务器部署路径（默认: /var/www/html/frontend）

set -e

# 默认配置
BUILD_ONLY=false
UPLOAD_ONLY=false
SERVER="120.27.198.74"
USER="root"
DEPLOY_PATH="/var/www/html/frontend"
FRONTEND_DIR="frontend"

# 解析参数
for arg in "$@"; do
    case $arg in
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --upload-only)
            UPLOAD_ONLY=true
            shift
            ;;
        --server=*)
            SERVER="${arg#*=}"
            shift
            ;;
        --user=*)
            USER="${arg#*=}"
            shift
            ;;
        --path=*)
            DEPLOY_PATH="${arg#*=}"
            shift
            ;;
        *)
            echo "未知参数: $arg"
            exit 1
            ;;
    esac
done

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Node.js
check_node() {
    if ! command -v node &> /dev/null; then
        echo_error "未找到 Node.js，请先安装 Node.js 16+"
        exit 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        echo_error "Node.js 版本过低，需要 16+，当前版本: $(node -v)"
        exit 1
    fi
    
    echo_info "Node.js 版本: $(node -v)"
}

# 构建项目
build_project() {
    echo_info "开始构建前端项目..."
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo_error "前端目录不存在: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # 检查 package.json
    if [ ! -f "package.json" ]; then
        echo_error "未找到 package.json"
        exit 1
    fi
    
    # 安装依赖（如果需要）
    if [ ! -d "node_modules" ]; then
        echo_info "安装依赖..."
        npm install
    fi
    
    # 构建
    echo_info "执行构建..."
    npm run build
    
    if [ ! -d "build" ]; then
        echo_error "构建失败，未找到 build 目录"
        exit 1
    fi
    
    echo_info "构建完成！"
    cd ..
}

# 上传文件
upload_files() {
    if [ -z "$SERVER" ]; then
        echo_error "请指定服务器地址: --server=IP"
        exit 1
    fi
    
    if [ ! -d "$FRONTEND_DIR/build" ]; then
        echo_error "构建目录不存在: $FRONTEND_DIR/build"
        echo_warn "请先运行构建: npm run build"
        exit 1
    fi
    
    echo_info "准备上传文件到服务器..."
    echo_info "服务器: $USER@$SERVER"
    echo_info "部署路径: $DEPLOY_PATH"
    
    # 确认
    read -p "确认上传? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo_warn "已取消上传"
        exit 0
    fi
    
    # 创建远程目录
    echo_info "创建远程目录..."
    ssh "$USER@$SERVER" "mkdir -p $DEPLOY_PATH"
    
    # 上传文件
    echo_info "上传文件..."
    scp -r "$FRONTEND_DIR/build"/* "$USER@$SERVER:$DEPLOY_PATH/"
    
    echo_info "上传完成！"
    echo_info "请在服务器上配置 Nginx 并重启服务"
}

# 主流程
main() {
    echo_info "=== 前端部署脚本 ==="
    
    if [ "$UPLOAD_ONLY" = false ]; then
        check_node
        build_project
    fi
    
    if [ "$BUILD_ONLY" = false ]; then
        upload_files
    else
        echo_info "仅构建模式，跳过上传"
        echo_info "构建文件位于: $FRONTEND_DIR/build"
    fi
}

main

