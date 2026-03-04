FROM python:3.11-slim

# Set timezone to Asia/Shanghai
ENV TZ=Asia/Shanghai
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Use Aliyun mirror (optimized for China)
RUN echo "Types: deb\n\
URIs: https://mirrors.aliyun.com/debian/\n\
Suites: bookworm bookworm-updates\n\
Components: main contrib non-free non-free-firmware\n\
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg\n\
\n\
Types: deb\n\
URIs: https://mirrors.aliyun.com/debian-security/\n\
Suites: bookworm-security\n\
Components: main contrib non-free non-free-firmware\n\
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg" \
> /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 代码通过 volume 挂载，不再复制进镜像
# 启动命令在 docker-compose.yml 中配置
