@echo off
echo 正在启动资讯后端服务...
echo.
echo 请等待服务启动完成，看到 "Started StockApplication" 表示启动成功
echo 按 Ctrl+C 可以停止服务
echo.
mvn spring-boot:run
pause

