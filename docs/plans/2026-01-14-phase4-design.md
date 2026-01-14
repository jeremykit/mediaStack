# 直播录制与点播系统 - 第四阶段设计

## 1. 阶段范围

### 前置依赖
- 第一至三阶段全部完成

### 包含功能
- 自动录制（检测流自动开始）
- 视频片段分享（M3U8 时间裁剪）
- 完善的日志与审计
- 服务器状态监控增强
- Webhook 告警通知

## 2. 数据模型扩展

### 2.1 LiveSource 扩展字段
| 字段 | 类型 | 说明 |
|------|------|------|
| auto_record | BOOLEAN | 是否自动录制 |
| check_interval | INTEGER | 检测间隔(秒)，默认60 |
| last_check_at | DATETIME | 上次检测时间 |
| stream_status | ENUM | online/offline/unknown |

### 2.2 视频片段分享 (VideoClip)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(16) | 短链ID |
| video_id | INTEGER | 视频ID |
| start_time | INTEGER | 开始时间(秒) |
| end_time | INTEGER | 结束时间(秒) |
| created_at | DATETIME | 创建时间 |
| expires_at | DATETIME | 过期时间 |
| view_count | INTEGER | 访问次数 |

### 2.3 操作日志 (OperationLog)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| admin_id | INTEGER | 操作人ID |
| action | VARCHAR(32) | 操作类型 |
| target_type | VARCHAR(32) | 目标类型 |
| target_id | INTEGER | 目标ID |
| detail | JSON | 操作详情 |
| ip_address | VARCHAR(45) | IP地址 |
| created_at | DATETIME | 操作时间 |

### 2.4 访问日志 (AccessLog)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| video_id | INTEGER | 视频ID |
| view_code | VARCHAR(12) | 使用的观看码 |
| ip_address | VARCHAR(45) | IP地址 |
| user_agent | VARCHAR(256) | 浏览器UA |
| watch_duration | INTEGER | 观看时长(秒) |
| created_at | DATETIME | 访问时间 |

### 2.5 Webhook 配置 (WebhookConfig)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(64) | 配置名称 |
| url | VARCHAR(512) | Webhook URL |
| events | JSON | 订阅事件列表 |
| is_active | BOOLEAN | 是否启用 |
| secret | VARCHAR(64) | 签名密钥 |
| created_at | DATETIME | 创建时间 |

## 3. API 设计

### 3.1 自动录制
| 方法 | 路径 | 说明 |
|------|------|------|
| PUT | /api/sources/{id}/auto-record | 设置自动录制 |
| GET | /api/sources/stream-status | 批量获取流状态 |

### 3.2 视频片段分享
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/videos/{id}/clips | 创建片段分享 |
| GET | /api/clips/{short_id} | 获取片段信息 |
| GET | /api/clips/{short_id}/play | 获取片段播放地址 |
| POST | /api/clips/{short_id}/audio | 生成片段音频 |
| GET | /api/videos/{id}/clips | 获取视频的所有片段 |
| DELETE | /api/clips/{short_id} | 删除片段 |

### 3.3 日志查询
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/logs/operations | 查询操作日志 |
| GET | /api/logs/access | 查询访问日志 |
| GET | /api/logs/access/stats | 访问统计 |

### 3.4 Webhook 管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/webhooks | 获取配置列表 |
| POST | /api/webhooks | 创建配置 |
| PUT | /api/webhooks/{id} | 更新配置 |
| DELETE | /api/webhooks/{id} | 删除配置 |
| POST | /api/webhooks/{id}/test | 测试发送 |

### 3.5 系统监控增强
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/system/status | 系统状态（含带宽、在线人数）|
| GET | /api/system/storage | 存储详情 |
| GET | /api/system/bandwidth | 实时带宽 |

## 4. 前端页面扩展

### 4.1 新增页面
- **操作日志** `/admin/logs/operations`
- **访问日志** `/admin/logs/access`
- **Webhook 管理** `/admin/webhooks`

### 4.2 页面修改
- **直播源管理** - 增加自动录制开关、流状态显示
- **视频详情页（管理员）** - 增加片段分享功能
- **系统状态** - 增加带宽监控、在线人数

## 5. 自动录制流程

```
┌─────────────────────────────────────┐
│ 定时任务 (每分钟)                    │
│ 检查所有 auto_record=true 的直播源   │
└────────────────┬────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│ 并发检测流状态                       │
│ FFprobe 探测 RTMP/HLS 地址          │
└────────────────┬────────────────────┘
                 ▼
         ┌───────┴───────┐
         │               │
         ▼               ▼
    流在线           流离线
    且未录制          或已录制
         │               │
         ▼               │
┌─────────────────┐      │
│ 自动开始录制     │      │
│ 创建 RecordTask │      │
└────────┬────────┘      │
         │               │
         └───────┬───────┘
                 ▼
┌─────────────────────────────────────┐
│ 更新 stream_status, last_check_at   │
└─────────────────────────────────────┘
```

## 6. 视频片段分享

### nginx-vod-module 时间裁剪
```
# 原始播放地址
/vod/video.mp4/index.m3u8

# 裁剪播放地址 (从60秒到180秒)
/vod/video.mp4/clipFrom/60000/clipTo/180000/index.m3u8
```

### 片段音频生成
```bash
ffmpeg -i input.mp4 \
  -ss 60 -to 180 \
  -vn \
  -acodec libmp3lame \
  -ab 128k \
  output_clip.mp3
```

## 7. Webhook 事件

| 事件 | 触发条件 |
|------|----------|
| recording.started | 录制开始 |
| recording.completed | 录制完成 |
| recording.failed | 录制失败 |
| storage.warning | 磁盘使用率 >= 90% |
| stream.online | 直播源上线 |
| stream.offline | 直播源离线 |

### Webhook 请求格式
```json
{
  "event": "recording.completed",
  "timestamp": "2026-01-14T12:00:00Z",
  "data": {
    "task_id": 123,
    "source_name": "直播源1",
    "file_path": "/data/videos/xxx.mp4",
    "duration": 3600
  }
}
```

## 8. 日志保留策略

| 日志类型 | 默认保留 | 可配置 |
|----------|----------|--------|
| 操作日志 | 90天 | 是 |
| 访问日志 | 90天 | 是 |

## 9. 实现任务清单

1. 数据库迁移 - 新增表结构
2. 流状态检测服务（FFprobe）
3. 自动录制调度器
4. 视频片段分享 API
5. nginx-vod-module 裁剪配置
6. 片段音频生成服务
7. 操作日志中间件
8. 访问日志记录
9. Webhook 服务
10. 前端自动录制配置
11. 前端片段分享组件
12. 前端日志查询页面
13. 前端 Webhook 管理页面
14. 系统监控增强（带宽、在线人数）
