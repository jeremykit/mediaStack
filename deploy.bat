@echo off
REM MediaStack 部署脚本 (Windows)

echo =========================================
echo MediaStack 部署脚本
echo =========================================

REM 停止容器
echo [1/4] 停止现有容器...
docker compose down

REM 拉取最新代码
echo [2/4] 拉取最新代码...
git pull

REM 启动容器
echo [3/4] 启动容器...
docker compose up -d

REM 显示日志
echo [4/4] 显示日志 (Ctrl+C 退出日志查看，容器继续运行)...
echo =========================================
docker compose logs -f
