FROM alfg/nginx-vod-module:latest

# 配置文件通过 volume 挂载，不再复制进镜像

EXPOSE 80

CMD ["/usr/local/nginx/sbin/nginx", "-g", "daemon off;"]
