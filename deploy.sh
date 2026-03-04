#!/bin/bash
# MediaStack 部署脚本

set -e

echo "========================================="
echo "MediaStack 部署脚本"
echo "========================================="

# 拉取最新代码
echo "[1/4] 拉取最新代码..."
git pull

# 停止容器
echo "[2/4] 停止现有容器..."
docker compose down

# 启动容器
echo "[3/4] 启动容器..."
docker compose up -d

# 显示日志
echo "[4/4] 显示日志 (Ctrl+C 退出日志查看，容器继续运行)..."
echo "========================================="
docker compose logs -f
