FROM alfg/nginx-vod-module:latest

COPY nginx.conf /usr/local/nginx/conf/nginx.conf

EXPOSE 80

CMD ["/usr/local/nginx/sbin/nginx", "-g", "daemon off;"]
