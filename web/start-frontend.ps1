Write-Host "Starting React Frontend..." -ForegroundColor Green

# 切换到前端目录
Set-Location -Path "frontend"

# 检查node_modules是否存在，不存在则安装依赖
if (!(Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# 启动开发服务器
Write-Host "Starting development server..." -ForegroundColor Green
npm start
