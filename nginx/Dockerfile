FROM alfg/nginx-vod-module:latest

# Set timezone to Asia/Shanghai
ENV TZ=Asia/Shanghai
RUN apk add --no-cache tzdata



EXPOSE 80

# 设置 entrypoint 来处理环境变量
CMD ["/usr/local/nginx/sbin/nginx", "-g", "daemon off;"]
