# MediaStack - 直播录制与点播系统

## 功能
- 直播流录制（RTMP/HLS 拉流）
- 录像在线点播播放
- 定时录制任务

## 技术栈
- 后端：FastAPI + SQLite
- 前端：Vue 3 + Element Plus
- 流媒体：FFmpeg + nginx-vod-module

## 开发

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 部署
```bash
docker-compose up -d
```
