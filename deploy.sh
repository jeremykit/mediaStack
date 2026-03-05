#!/bin/bash
# MediaStack 部署脚本

set -e

echo "========================================="
echo "MediaStack 部署脚本"
echo "========================================="

# 停止容器
echo "[1/6] 停止现有容器..."
docker compose down

# 拉取最新代码
echo "[2/6] 拉取最新代码..."
git pull

# 编译前端代码
echo "[3/6] 编译前端代码..."
cd frontend && npm run build && cd ..

# 构建镜像
echo "[4/6] 构建镜像..."
docker compose build

# 启动容器
echo "[5/6] 启动容器..."
docker compose up -d

# 显示日志
echo "[6/6] 显示日志 (Ctrl+C 退出日志查看，容器继续运行)..."
echo "========================================="
docker compose logs -f
