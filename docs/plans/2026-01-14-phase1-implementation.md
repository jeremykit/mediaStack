# 第一阶段实现计划

## 概述
基于 `2026-01-14-phase1-design.md` 设计文档，本计划将第一阶段拆分为可独立验证的实现任务。

## 依赖关系图

```
[1. 项目初始化]
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
[2. 后端基础架构]   [3. 前端基础架构]   [4. Docker 基础配置]
       │                  │
       ▼                  │
[5. 数据库模型]           │
       │                  │
       ├──────────────────┤
       ▼                  │
[6. 认证模块]             │
       │                  │
       ├──────────────────┤
       ▼                  ▼
[7. 直播源管理 API] ──► [8. 直播源管理前端]
       │                  │
       ▼                  ▼
[9. 录制服务]      ──► [10. 录制控制前端]
       │                  │
       ▼                  ▼
[11. 定时任务服务] ──► [12. 定时计划前端]
       │                  │
       ▼                  ▼
[13. 视频管理 API] ──► [14. 视频播放前端]
       │                  │
       ▼                  ▼
[15. 系统状态 API] ──► [16. 系统状态前端]
       │                  │
       └──────────────────┤
                          ▼
                   [17. nginx-vod 配置]
                          │
                          ▼
                   [18. Docker Compose 完整配置]
                          │
                          ▼
                   [19. 集成测试]
```

---

## 任务清单

### 1. 项目初始化
**目标**: 创建项目目录结构和基础配置文件

**交付物**:
- `backend/` 目录结构
- `frontend/` 目录结构
- `.gitignore` 更新
- `README.md` 项目说明

**验收标准**:
- [ ] 目录结构符合设计文档第8节
- [ ] `.gitignore` 包含 Python/Node/IDE 忽略规则

---

### 2. 后端基础架构
**目标**: 搭建 FastAPI 应用骨架

**依赖**: 任务 1

**交付物**:
- `backend/app/main.py` - FastAPI 应用入口
- `backend/app/config.py` - 配置管理（Pydantic Settings）
- `backend/requirements.txt` - Python 依赖
- `backend/.env.example` - 环境变量模板

**验收标准**:
- [ ] `uvicorn app.main:app --reload` 启动成功
- [ ] 访问 `/docs` 显示 Swagger UI
- [ ] 配置从环境变量加载

**依赖包**:
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
apscheduler>=3.10.0
python-multipart>=0.0.6
```

---

### 3. 前端基础架构
**目标**: 搭建 Vue 3 + Element Plus 应用骨架

**依赖**: 任务 1

**交付物**:
- `frontend/` - Vite + Vue 3 + TypeScript 项目
- 路由配置（Vue Router）
- 状态管理（Pinia）
- Element Plus 集成
- Axios HTTP 客户端封装

**验收标准**:
- [ ] `npm run dev` 启动成功
- [ ] Element Plus 组件可用
- [ ] 路由跳转正常

**依赖包**:
```json
{
  "vue": "^3.4.0",
  "vue-router": "^4.2.0",
  "pinia": "^2.1.0",
  "element-plus": "^2.5.0",
  "axios": "^1.6.0",
  "@element-plus/icons-vue": "^2.3.0"
}
```

---

### 4. Docker 基础配置
**目标**: 创建开发环境 Docker 配置

**依赖**: 任务 2, 3

**交付物**:
- `backend/Dockerfile` - 后端镜像
- `frontend/Dockerfile` - 前端镜像（开发用）
- `docker-compose.dev.yml` - 开发环境编排

**验收标准**:
- [ ] `docker-compose -f docker-compose.dev.yml up` 启动成功
- [ ] 后端 API 可访问
- [ ] 前端页面可访问

---

### 5. 数据库模型
**目标**: 实现 SQLAlchemy 数据模型

**依赖**: 任务 2

**交付物**:
- `backend/app/database.py` - 数据库连接
- `backend/app/models/__init__.py`
- `backend/app/models/admin.py` - Admin 模型
- `backend/app/models/source.py` - LiveSource 模型
- `backend/app/models/task.py` - RecordTask 模型
- `backend/app/models/schedule.py` - Schedule 模型
- `backend/app/models/video.py` - VideoFile 模型

**验收标准**:
- [ ] 应用启动时自动创建表
- [ ] 模型关系正确（外键约束）
- [ ] 枚举类型定义正确

---

### 6. 认证模块
**目标**: 实现 JWT 认证

**依赖**: 任务 5

**交付物**:
- `backend/app/schemas/auth.py` - 请求/响应模型
- `backend/app/api/auth.py` - 认证路由
- `backend/app/api/deps.py` - 依赖注入（get_current_user）
- 初始管理员账号创建脚本

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 登录，返回 JWT |
| POST | /api/auth/logout | 登出（客户端清除 token）|
| GET | /api/auth/me | 获取当前用户信息 |

**验收标准**:
- [ ] 登录成功返回 JWT token
- [ ] 受保护路由需要有效 token
- [ ] token 过期返回 401

---

### 7. 直播源管理 API
**目标**: 实现直播源 CRUD

**依赖**: 任务 6

**交付物**:
- `backend/app/schemas/source.py` - 请求/响应模型
- `backend/app/api/sources.py` - 直播源路由
- `backend/app/services/stream_checker.py` - 流状态检测

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/sources | 获取列表 |
| POST | /api/sources | 创建 |
| GET | /api/sources/{id} | 获取详情 |
| PUT | /api/sources/{id} | 更新 |
| DELETE | /api/sources/{id} | 删除 |
| GET | /api/sources/{id}/status | 检测在线状态 |

**验收标准**:
- [ ] CRUD 操作正常
- [ ] 流状态检测返回 online/offline
- [ ] 删除时检查是否有进行中的录制

---

### 8. 直播源管理前端
**目标**: 实现直播源管理页面

**依赖**: 任务 3, 7

**交付物**:
- `frontend/src/views/admin/Sources.vue` - 列表页
- `frontend/src/components/SourceForm.vue` - 表单组件
- `frontend/src/api/sources.ts` - API 调用

**验收标准**:
- [ ] 列表展示直播源
- [ ] 新增/编辑表单验证
- [ ] 删除确认对话框
- [ ] 状态检测按钮

---

### 9. 录制服务
**目标**: 实现 FFmpeg 录制核心逻辑

**依赖**: 任务 7

**交付物**:
- `backend/app/services/recorder.py` - 录制服务
- `backend/app/schemas/task.py` - 请求/响应模型
- `backend/app/api/tasks.py` - 录制任务路由

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/sources/{id}/record/start | 开始录制 |
| POST | /api/sources/{id}/record/stop | 停止录制 |
| GET | /api/tasks | 获取任务列表 |
| GET | /api/tasks/{id} | 获取任务详情 |

**录制逻辑**:
1. 创建 RecordTask 记录（status=pending）
2. 生成输出文件路径：`{storage_path}/{source_name}_{YYYYMMDD_HHmmss}.mp4`
3. 启动 FFmpeg 子进程（异步）
4. 更新状态为 recording
5. 监控进程退出
6. 完成后更新状态、文件大小、时长
7. 生成缩略图
8. 创建 VideoFile 记录

**验收标准**:
- [ ] 手动开始录制成功
- [ ] 手动停止录制成功
- [ ] 录制中断自动保存已录制内容
- [ ] 文件命名符合规范
- [ ] 缩略图自动生成

---

### 10. 录制控制前端
**目标**: 实现录制任务管理页面

**依赖**: 任务 8, 9

**交付物**:
- `frontend/src/views/admin/Tasks.vue` - 任务列表页
- `frontend/src/api/tasks.ts` - API 调用

**验收标准**:
- [ ] 显示录制任务列表
- [ ] 状态实时更新（轮询或 WebSocket）
- [ ] 直播源页面可开始/停止录制

---

### 11. 定时任务服务
**目标**: 实现 APScheduler 定时录制

**依赖**: 任务 9

**交付物**:
- `backend/app/services/scheduler.py` - 定时任务服务
- `backend/app/schemas/schedule.py` - 请求/响应模型
- `backend/app/api/schedules.py` - 定时计划路由

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/schedules | 获取列表 |
| POST | /api/schedules | 创建 |
| PUT | /api/schedules/{id} | 更新 |
| DELETE | /api/schedules/{id} | 删除 |

**定时逻辑**:
1. 应用启动时加载所有 is_active=true 的计划
2. 使用 APScheduler CronTrigger 解析 cron 表达式
3. 触发时检查直播源是否已在录制
4. 已在录制则跳过，否则开始录制
5. 更新 last_run_at 和 next_run_at

**验收标准**:
- [ ] cron 表达式解析正确
- [ ] 定时触发录制
- [ ] 冲突时跳过
- [ ] 应用重启后计划恢复

---

### 12. 定时计划前端
**目标**: 实现定时计划管理页面

**依赖**: 任务 8, 11

**交付物**:
- `frontend/src/views/admin/Schedules.vue` - 列表页
- `frontend/src/components/ScheduleForm.vue` - 表单组件
- `frontend/src/api/schedules.ts` - API 调用

**验收标准**:
- [ ] 列表展示定时计划
- [ ] cron 表达式输入（带提示）
- [ ] 显示下次执行时间
- [ ] 启用/禁用开关

---

### 13. 视频管理 API
**目标**: 实现视频文件管理

**依赖**: 任务 9

**交付物**:
- `backend/app/schemas/video.py` - 请求/响应模型
- `backend/app/api/videos.py` - 视频路由

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/videos | 获取列表（支持搜索、分页）|
| GET | /api/videos/{id} | 获取详情 |
| PUT | /api/videos/{id} | 更新信息 |
| DELETE | /api/videos/{id} | 删除（含文件）|
| GET | /api/videos/{id}/play | 获取 HLS 播放地址 |
| POST | /api/videos/{id}/view | 增加观看次数 |

**验收标准**:
- [ ] 列表支持搜索、分页
- [ ] 删除时同时删除文件
- [ ] 播放地址返回 nginx-vod-module 格式

---

### 14. 视频播放前端
**目标**: 实现视频列表和播放页面

**依赖**: 任务 3, 13

**交付物**:
- `frontend/src/views/Home.vue` - 首页视频列表
- `frontend/src/views/VideoDetail.vue` - 视频详情页
- `frontend/src/views/admin/Videos.vue` - 管理页面
- `frontend/src/components/VideoCard.vue` - 视频卡片
- `frontend/src/components/VideoPlayer.vue` - 播放器组件
- `frontend/src/api/videos.ts` - API 调用

**验收标准**:
- [ ] 首页展示视频卡片（缩略图、标题、时长、观看次数）
- [ ] 搜索功能
- [ ] 播放器支持 HLS
- [ ] 倍速播放（0.5x/1x/1.5x/2x）
- [ ] 管理页面可编辑/删除

---

### 15. 系统状态 API
**目标**: 实现系统监控接口

**依赖**: 任务 2

**交付物**:
- `backend/app/schemas/system.py` - 响应模型
- `backend/app/api/system.py` - 系统路由

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/system/status | 获取系统状态 |

**返回数据**:
```json
{
  "cpu_percent": 45.2,
  "memory_percent": 68.5,
  "disk_total": 107374182400,
  "disk_used": 53687091200,
  "disk_free": 53687091200,
  "disk_percent": 50.0
}
```

**验收标准**:
- [ ] 返回 CPU/内存/磁盘使用率
- [ ] 数据实时准确

---

### 16. 系统状态前端
**目标**: 实现系统状态展示

**依赖**: 任务 3, 15

**交付物**:
- `frontend/src/views/admin/System.vue` - 系统状态页
- `frontend/src/components/SystemStatus.vue` - 状态组件（顶部栏）

**验收标准**:
- [ ] 顶部栏显示关键指标
- [ ] 系统页面详细展示
- [ ] 定时刷新（30秒）

---

### 17. nginx-vod-module 配置
**目标**: 配置 nginx 实现 MP4 转 HLS

**依赖**: 任务 13

**交付物**:
- `nginx/nginx.conf` - nginx 配置
- `nginx/Dockerfile` - 包含 vod-module 的镜像

**配置要点**:
```nginx
location /vod/ {
    vod hls;
    vod_mode local;
    vod_align_segments_to_key_frames on;
    alias /data/videos/;
}
```

**验收标准**:
- [ ] MP4 文件可通过 HLS 播放
- [ ] 支持 seek（拖动进度条）

---

### 18. Docker Compose 完整配置
**目标**: 完成生产环境部署配置

**依赖**: 任务 4, 17

**交付物**:
- `docker-compose.yml` - 生产环境编排
- `.env.example` - 环境变量模板
- 部署文档

**服务清单**:
- nginx（含 vod-module）
- backend（FastAPI）
- volumes（数据库 + 视频存储）

**验收标准**:
- [ ] 一键启动所有服务
- [ ] 数据持久化
- [ ] 前端通过 nginx 代理访问后端

---

### 19. 集成测试
**目标**: 端到端功能验证

**依赖**: 任务 1-18

**测试场景**:
1. 管理员登录
2. 创建直播源
3. 检测直播源状态
4. 手动开始录制
5. 手动停止录制
6. 查看录制文件
7. 播放视频
8. 创建定时计划
9. 等待定时触发
10. 删除视频

**验收标准**:
- [ ] 所有场景通过
- [ ] 无明显 bug
- [ ] 性能可接受

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| FFmpeg 录制中断 | 数据丢失 | 使用 `-movflags +faststart` 确保部分可播放 |
| nginx-vod-module 编译复杂 | 部署困难 | 使用预编译 Docker 镜像 |
| 定时任务持久化 | 重启丢失 | APScheduler 使用 SQLite 作为 jobstore |
| 大文件播放卡顿 | 用户体验差 | nginx-vod 分片 + CDN（后续优化）|

---

## 技术决策记录

### TD-001: 录制进程管理
**决策**: 使用 Python subprocess + asyncio 管理 FFmpeg 进程
**原因**: 简单直接，无需额外依赖
**替代方案**: Celery（过重）、FFmpeg Python 绑定（不成熟）

### TD-002: 定时任务框架
**决策**: APScheduler
**原因**: 轻量、支持 cron、可持久化
**替代方案**: Celery Beat（需要 Redis）、系统 cron（不便管理）

### TD-003: 视频播放方案
**决策**: nginx-vod-module 实时转 HLS
**原因**: 无需预转码、支持 seek、节省存储
**替代方案**: 预转码 HLS（占用存储）、直接播放 MP4（不支持大文件 seek）

### TD-004: 前端播放器
**决策**: Video.js + videojs-http-streaming
**原因**: 成熟稳定、HLS 支持好、可定制
**替代方案**: DPlayer（功能较少）、hls.js 直接使用（需要更多封装）
