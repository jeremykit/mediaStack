#!/bin/bash
# MediaStack 部署脚本

set -e

echo "========================================="
echo "MediaStack 部署脚本"
echo "========================================="

# 停止容器
echo "[1/5] 停止现有容器..."
docker compose down

# 拉取最新代码
echo "[2/5] 拉取最新代码..."
git pull

# 构建镜像
echo "[3/5] 构建镜像..."
docker compose build

# 启动容器
echo "[4/5] 启动容器..."
docker compose up -d

# 显示日志
echo "[5/5] 显示日志 (Ctrl+C 退出日志查看，容器继续运行)..."
echo "========================================="
docker compose logs -f
