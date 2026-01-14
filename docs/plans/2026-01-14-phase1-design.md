# 直播录制与点播系统 - 第一阶段设计

## 1. 阶段范围

### 包含功能
- 直播源管理（RTMP/HLS 拉流）
- 手动录制控制（开始/停止）
- 定时录制（cron 表达式）
- 基础点播播放
- 管理员登录 + 文件管理

### 不包含（后续阶段）
- 自动录制（检测流自动开始）
- 审核流程（录制完成直接可播放）
- 观看码系统
- 文件上传功能
- 音频提取/下载
- 扩展信息（关联图片/文本/链接）

## 2. 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                      Nginx                               │
│  ┌─────────────┐  ┌─────────────────────────────────┐   │
│  │ 静态文件     │  │ nginx-vod-module                │   │
│  │ (Vue 前端)   │  │ (MP4 → HLS 实时转封装)          │   │
│  └─────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI 后端                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 直播源管理   │  │ 录制任务管理 │  │ 文件管理    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│  ┌─────────────┐  ┌─────────────┐                       │
│  │ 定时任务     │  │ 用户认证    │                       │
│  │ (APScheduler)│  │ (JWT)      │                       │
│  └─────────────┘  └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ SQLite   │ │ FFmpeg   │ │ 文件存储  │
        │ 数据库    │ │ 录制进程  │ │ (MP4)    │
        └──────────┘ └──────────┘ └──────────┘
```

## 3. 数据模型

### 3.1 直播源 (LiveSource)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(64) | 直播源名称 |
| protocol | ENUM | rtmp / hls |
| url | VARCHAR(512) | 拉流地址 |
| retention_days | INTEGER | 保留天数，默认365 |
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 3.2 录制任务 (RecordTask)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| source_id | INTEGER | 关联直播源 |
| status | ENUM | pending/recording/completed/failed/interrupted |
| started_at | DATETIME | 开始时间 |
| ended_at | DATETIME | 结束时间 |
| file_path | VARCHAR(512) | 录制文件路径 |
| file_size | BIGINT | 文件大小(字节) |
| duration | INTEGER | 时长(秒) |
| error_message | TEXT | 错误信息 |

### 3.3 定时计划 (Schedule)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| source_id | INTEGER | 关联直播源 |
| cron_expr | VARCHAR(64) | cron 表达式 |
| is_active | BOOLEAN | 是否启用 |
| last_run_at | DATETIME | 上次执行时间 |
| next_run_at | DATETIME | 下次执行时间 |

### 3.4 视频文件 (VideoFile)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | INTEGER | 关联录制任务(可空) |
| title | VARCHAR(128) | 标题 |
| file_path | VARCHAR(512) | 文件路径 |
| file_size | BIGINT | 文件大小 |
| duration | INTEGER | 时长(秒) |
| thumbnail | VARCHAR(512) | 缩略图路径 |
| view_count | INTEGER | 观看次数 |
| source_type | ENUM | recorded / uploaded |
| created_at | DATETIME | 创建时间 |

### 3.5 管理员 (Admin)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(32) | 用户名 |
| password_hash | VARCHAR(128) | 密码哈希 |
| created_at | DATETIME | 创建时间 |
| last_login_at | DATETIME | 最后登录时间 |

## 4. API 设计

### 4.1 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 管理员登录 |
| POST | /api/auth/logout | 登出 |
| GET | /api/auth/me | 获取当前用户信息 |

### 4.2 直播源管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/sources | 获取直播源列表 |
| POST | /api/sources | 创建直播源 |
| PUT | /api/sources/{id} | 更新直播源 |
| DELETE | /api/sources/{id} | 删除直播源 |
| GET | /api/sources/{id}/status | 检测直播源在线状态 |

### 4.3 录制控制
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/sources/{id}/record/start | 开始录制 |
| POST | /api/sources/{id}/record/stop | 停止录制 |
| GET | /api/tasks | 获取录制任务列表 |
| GET | /api/tasks/{id} | 获取任务详情 |

### 4.4 定时计划
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/schedules | 获取定时计划列表 |
| POST | /api/schedules | 创建定时计划 |
| PUT | /api/schedules/{id} | 更新定时计划 |
| DELETE | /api/schedules/{id} | 删除定时计划 |

### 4.5 视频管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/videos | 获取视频列表 |
| GET | /api/videos/{id} | 获取视频详情 |
| PUT | /api/videos/{id} | 更新视频信息 |
| DELETE | /api/videos/{id} | 删除视频 |
| GET | /api/videos/{id}/play | 获取播放地址(HLS) |

### 4.6 系统
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/system/status | 获取系统状态(CPU/内存/磁盘) |

## 5. 前端页面

### 5.1 页面清单
1. **登录页** `/login`
2. **首页/视频列表** `/` - 视频卡片列表，支持搜索
3. **视频详情页** `/video/:id` - 播放器 + 视频信息
4. **管理后台**
   - 直播源管理 `/admin/sources`
   - 录制任务 `/admin/tasks`
   - 定时计划 `/admin/schedules`
   - 视频管理 `/admin/videos`
   - 系统状态 `/admin/system`

### 5.2 组件结构
```
src/
├── views/
│   ├── Login.vue
│   ├── Home.vue
│   ├── VideoDetail.vue
│   └── admin/
│       ├── Sources.vue
│       ├── Tasks.vue
│       ├── Schedules.vue
│       ├── Videos.vue
│       └── System.vue
├── components/
│   ├── VideoCard.vue
│   ├── VideoPlayer.vue
│   ├── SourceForm.vue
│   ├── ScheduleForm.vue
│   └── SystemStatus.vue
├── api/
│   └── index.ts
├── stores/
│   └── auth.ts
└── router/
    └── index.ts
```

## 6. 录制流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 手动触发     │     │ 定时触发     │     │ 检测流状态   │
│ /record/start│     │ APScheduler │     │ (可选)      │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                  ┌─────────────────┐
                  │ 创建 RecordTask  │
                  │ status=pending  │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │ 启动 FFmpeg 进程 │
                  │ status=recording│
                  └────────┬────────┘
                           ▼
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
     ┌─────────────────┐      ┌─────────────────┐
     │ 正常结束         │      │ 异常中断         │
     │ status=completed│      │ status=failed   │
     └────────┬────────┘      └────────┬────────┘
              │                        │
              └────────────┬───────────┘
                           ▼
                  ┌─────────────────┐
                  │ 创建 VideoFile   │
                  │ 生成缩略图       │
                  └─────────────────┘
```

## 7. FFmpeg 录制命令

### RTMP 拉流录制
```bash
ffmpeg -i rtmp://source.url/stream \
  -c copy \
  -f mp4 \
  -movflags +faststart \
  output.mp4
```

### HLS 拉流录制
```bash
ffmpeg -i https://source.url/playlist.m3u8 \
  -c copy \
  -f mp4 \
  -movflags +faststart \
  output.mp4
```

## 8. 目录结构

```
mediaStack/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── sources.py
│   │   │   ├── tasks.py
│   │   │   ├── schedules.py
│   │   │   ├── videos.py
│   │   │   └── system.py
│   │   └── services/
│   │       ├── recorder.py
│   │       └── scheduler.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
└── docs/
```

## 9. 部署配置

### docker-compose.yml 核心服务
- **nginx**: 静态文件 + nginx-vod-module
- **backend**: FastAPI 应用
- **volumes**: 数据库文件 + 录制文件存储

## 10. 后续阶段规划

### 第二阶段
- 文件上传功能
- 分类与标签管理
- 观看码系统

### 第三阶段
- 审核流程
- 扩展信息（图片/文本/链接）
- 音频提取与下载

### 第四阶段
- 自动录制（检测流）
- 视频片段分享
- 完善的日志与审计
