Write-Host "Starting Spring Boot Backend..." -ForegroundColor Green

# 切换到后端目录
Set-Location -Path "backend"

# 启动Spring Boot应用
Write-Host "Running Maven Spring Boot application..." -ForegroundColor Green
mvn spring-boot:run
