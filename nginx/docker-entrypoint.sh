#!/bin/sh
# nginx vod_base_url 环境变量替换脚本

if [ -n "$VOD_BASE_URL" ]; then
    echo "Setting vod_base_url to: $VOD_BASE_URL"
    # 从模板生成 nginx.conf，替换 VOD_BASE_URL 变量
    envsubst '$VOD_BASE_URL' < /usr/local/nginx/conf/nginx.conf.template > /usr/local/nginx/conf/nginx.conf
else
    # 如果没有设置环境变量，直接使用模板（使用默认值）
    echo "Using default vod_base_url from template"
    envsubst '$VOD_BASE_URL' < /usr/local/nginx/conf/nginx.conf.template > /usr/local/nginx/conf/nginx.conf
fi

# 执行 CMD 中的命令（启动 nginx）
exec "$@"
