#!/bin/sh
# nginx vod_base_url 环境变量替换脚本

# 设置默认值
VOD_BASE_URL="${VOD_BASE_URL:-https://media.jidan.cool}"

echo "Setting vod_base_url to: $VOD_BASE_URL"

# 从模板生成 nginx.conf，只替换 VOD_BASE_URL 变量
export VOD_BASE_URL
envsubst '$VOD_BASE_URL' < /usr/local/nginx/conf/nginx.conf.template > /usr/local/nginx/conf/nginx.conf

# 执行 CMD 中的命令（启动 nginx）
exec "$@"
