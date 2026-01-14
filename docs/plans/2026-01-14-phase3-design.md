# 直播录制与点播系统 - 第三阶段设计

## 1. 阶段范围

### 前置依赖
- 第一阶段完成（直播源管理、录制、基础播放）
- 第二阶段完成（上传、分类、标签、观看码）

### 包含功能
- 录制文件审核流程
- 扩展信息管理（关联图片/文本/链接）
- 音频提取与下载
- 视频封面管理

### 不包含（后续阶段）
- 自动录制（检测流）
- 视频片段分享

## 2. 数据模型扩展

### 2.1 VideoFile 扩展字段
| 字段 | 类型 | 说明 |
|------|------|------|
| status | ENUM | pending/published/offline |
| reviewed_at | DATETIME | 审核时间 |
| reviewed_by | INTEGER | 审核人ID |

### 2.2 关联图片 (VideoImage)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| video_id | INTEGER | 视频ID |
| image_path | VARCHAR(512) | 图片路径 |
| sort_order | INTEGER | 排序 |
| created_at | DATETIME | 创建时间 |

### 2.3 关联文本 (VideoText)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| video_id | INTEGER | 视频ID |
| title | VARCHAR(64) | 标题 |
| content | TEXT | 富文本内容 |
| sort_order | INTEGER | 排序 |
| created_at | DATETIME | 创建时间 |

### 2.4 关联链接 (VideoLink)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| video_id | INTEGER | 视频ID |
| title | VARCHAR(64) | 链接标题 |
| url | VARCHAR(512) | 链接地址 |
| sort_order | INTEGER | 排序 |
| created_at | DATETIME | 创建时间 |

### 2.5 音频提取任务 (AudioExtractTask)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| video_id | INTEGER | 视频ID |
| status | ENUM | pending/processing/completed/failed |
| output_path | VARCHAR(512) | 输出文件路径 |
| format | VARCHAR(8) | mp3 |
| bitrate | VARCHAR(8) | 128k |
| created_at | DATETIME | 创建时间 |
| completed_at | DATETIME | 完成时间 |

## 3. API 设计

### 3.1 审核管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/videos/pending | 获取待审核列表 |
| POST | /api/videos/{id}/publish | 发布视频 |
| POST | /api/videos/{id}/offline | 下架视频 |
| POST | /api/videos/batch-publish | 批量发布 |
| POST | /api/videos/batch-offline | 批量下架 |

### 3.2 扩展信息
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/videos/{id}/images | 获取关联图片 |
| POST | /api/videos/{id}/images | 添加关联图片 |
| DELETE | /api/videos/{id}/images/{img_id} | 删除关联图片 |
| GET | /api/videos/{id}/texts | 获取关联文本 |
| POST | /api/videos/{id}/texts | 添加关联文本 |
| PUT | /api/videos/{id}/texts/{text_id} | 更新关联文本 |
| DELETE | /api/videos/{id}/texts/{text_id} | 删除关联文本 |
| GET | /api/videos/{id}/links | 获取关联链接 |
| POST | /api/videos/{id}/links | 添加关联链接 |
| DELETE | /api/videos/{id}/links/{link_id} | 删除关联链接 |

### 3.3 音频提取
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/videos/{id}/extract-audio | 提取音频 |
| GET | /api/videos/{id}/audio | 获取音频信息 |
| GET | /api/videos/{id}/audio/download | 下载音频 |

### 3.4 封面管理
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/videos/{id}/thumbnail/auto | 自动截取封面 |
| POST | /api/videos/{id}/thumbnail/upload | 上传封面 |
| POST | /api/videos/{id}/thumbnail/capture | 指定时间点截取 |

## 4. 前端页面扩展

### 4.1 新增页面
- **录制文件管理** `/admin/recordings` - 待审核/已发布/已下架筛选

### 4.2 页面修改
- **视频详情页** - 显示扩展信息（图片轮播、文本内容、外部链接）
- **视频管理** - 增加扩展信息编辑、审核操作
- **视频详情页** - 增加音频播放模式、音频下载按钮

## 5. 审核流程

```
┌─────────────────┐
│ 录制完成        │
│ status=pending  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 管理员编辑信息   │
│ - 标题/描述     │
│ - 分类/标签     │
│ - 扩展信息      │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 审核操作        │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ 发布   │ │ 拒绝   │
│published│ │ 保持   │
└────┬───┘ │pending │
     │     └────────┘
     ▼
┌─────────────────┐
│ 前台可见        │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 可下架          │
│ status=offline  │
└─────────────────┘
```

## 6. 音频提取规格

| 参数 | 默认值 |
|------|--------|
| 格式 | MP3 |
| 码率 | 128kbps |
| 采样率 | 44100Hz |
| 声道 | 立体声 |

### FFmpeg 命令
```bash
ffmpeg -i input.mp4 \
  -vn \
  -acodec libmp3lame \
  -ab 128k \
  -ar 44100 \
  -ac 2 \
  output.mp3
```

## 7. 实现任务清单

1. 数据库迁移 - 新增表结构、VideoFile 扩展字段
2. 审核状态管理 API
3. 批量审核 API
4. 关联图片 CRUD API + 图片上传
5. 关联文本 CRUD API
6. 关联链接 CRUD API
7. 音频提取服务（FFmpeg 异步任务）
8. 封面管理 API
9. 前端录制文件管理页面
10. 前端扩展信息编辑组件
11. 前端视频详情页扩展信息展示
12. 前端音频播放/下载功能
