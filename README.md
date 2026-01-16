# MediaStack - 直播录制与点播系统

## 功能
- 直播流录制（RTMP/HLS 拉流）
- 录像在线点播播放
- 定时录制任务

## 技术栈
- 后端：FastAPI + SQLite
- 前端：Vue 3 + Element Plus
- 流媒体：FFmpeg + nginx-vod-module

## 本地开发环境搭建

### 前置要求
- Python 3.10+
- Node.js 16+
- FFmpeg（用于录制功能）

### 后端开发

#### 1. 创建 Python 虚拟环境
```bash
cd backend
python -m venv venv
```

#### 2. 激活虚拟环境

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量（可选）
```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，修改配置（如数据库路径、管理员密码等）
```

#### 5. 启动后端服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将运行在 `http://localhost:8000`
- API 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/health`

#### 6. 退出虚拟环境
```bash
deactivate
```

### 前端开发

#### 1. 安装依赖
```bash
cd frontend
npm install
```

#### 2. 启动开发服务器
```bash
npm run dev
```

前端开发服务器将运行在 `http://localhost:5173`

#### 3. 构建生产版本
```bash
npm run build
```

### 本地开发说明

- **数据库**：默认使用 SQLite，数据库文件位于 `backend/data/db/mediastack.db`
- **录制文件存储**：默认存储在 `backend/data/videos/` 目录
- **点播播放**：本地开发环境不需要 nginx-vod-module，可以直接测试录制功能
- **默认管理员账号**：用户名 `admin`，密码 `admin123`（可通过环境变量修改）

## 部署

### 生产环境部署

1. 构建前端
```bash
cd frontend
npm install
npm run build
cd ..
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 设置安全的密钥和密码
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问 http://localhost
