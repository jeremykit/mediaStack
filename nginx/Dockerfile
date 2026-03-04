FROM alfg/nginx-vod-module:latest

# Set timezone to Asia/Shanghai
ENV TZ=Asia/Shanghai
RUN apk add --no-cache tzdata

# 复制环境变量处理脚本
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

# 设置 entrypoint 来处理环境变量
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/usr/local/nginx/sbin/nginx", "-g", "daemon off;"]
