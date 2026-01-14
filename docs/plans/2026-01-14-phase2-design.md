# 直播录制与点播系统 - 第二阶段设计

## 1. 阶段范围

### 前置依赖
- 第一阶段完成（直播源管理、录制、基础播放）

### 包含功能
- 文件上传（视频 MP4、音频 MP3/WAV/AAC/FLAC）
- 分片上传（大文件支持）
- 分类管理
- 标签管理
- 观看码系统

### 不包含（后续阶段）
- 审核流程
- 扩展信息（关联图片/文本/链接）
- 音频提取与下载

## 2. 数据模型扩展

### 2.1 分类 (Category)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(32) | 分类名称 |
| sort_order | INTEGER | 排序权重 |
| created_at | DATETIME | 创建时间 |

### 2.2 标签 (Tag)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(16) | 标签名称 |
| created_at | DATETIME | 创建时间 |

### 2.3 视频-标签关联 (VideoTag)
| 字段 | 类型 | 说明 |
|------|------|------|
| video_id | INTEGER | 视频ID |
| tag_id | INTEGER | 标签ID |

### 2.4 观看码 (ViewCode)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| code | VARCHAR(12) | 观看码（6-12位字母数字）|
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| expires_at | DATETIME | 过期时间（可空）|

### 2.5 观看码-分类关联 (ViewCodeCategory)
| 字段 | 类型 | 说明 |
|------|------|------|
| code_id | INTEGER | 观看码ID |
| category_id | INTEGER | 分类ID |

### 2.6 VideoFile 扩展字段
| 字段 | 类型 | 说明 |
|------|------|------|
| category_id | INTEGER | 分类ID（可空）|
| file_type | ENUM | video / audio |

### 2.7 上传任务 (UploadTask)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) | UUID |
| filename | VARCHAR(256) | 原始文件名 |
| file_size | BIGINT | 文件总大小 |
| chunk_size | INTEGER | 分片大小 |
| total_chunks | INTEGER | 总分片数 |
| uploaded_chunks | INTEGER | 已上传分片数 |
| status | ENUM | uploading/completed/failed |
| created_at | DATETIME | 创建时间 |

## 3. API 设计

### 3.1 文件上传
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload/init | 初始化上传任务 |
| POST | /api/upload/{task_id}/chunk | 上传分片 |
| POST | /api/upload/{task_id}/complete | 完成上传 |
| GET | /api/upload/{task_id}/status | 查询上传状态 |
| DELETE | /api/upload/{task_id} | 取消上传 |

### 3.2 分类管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/categories | 获取分类列表 |
| POST | /api/categories | 创建分类 |
| PUT | /api/categories/{id} | 更新分类 |
| DELETE | /api/categories/{id} | 删除分类 |

### 3.3 标签管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tags | 获取标签列表 |
| POST | /api/tags | 创建标签 |
| DELETE | /api/tags/{id} | 删除标签 |

### 3.4 观看码管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/view-codes | 获取观看码列表 |
| POST | /api/view-codes | 创建观看码 |
| PUT | /api/view-codes/{id} | 更新观看码 |
| DELETE | /api/view-codes/{id} | 删除观看码 |
| POST | /api/view-codes/verify | 验证观看码 |

### 3.5 VideoFile API 扩展
| 方法 | 路径 | 说明 |
|------|------|------|
| PUT | /api/videos/{id}/category | 设置分类 |
| PUT | /api/videos/{id}/tags | 设置标签 |

## 4. 前端页面扩展

### 4.1 新增页面
- **观看码输入页** `/verify` - 访客首次访问验证
- **上传页面** `/admin/upload` - 拖拽上传、进度显示
- **分类管理** `/admin/categories`
- **标签管理** `/admin/tags`
- **观看码管理** `/admin/view-codes`

### 4.2 页面修改
- **首页** - 增加分类筛选、标签筛选
- **视频管理** - 增加分类/标签编辑

## 5. 分片上传流程

```
┌─────────────┐
│ 选择文件    │
└──────┬──────┘
       ▼
┌─────────────────┐
│ POST /upload/init│
│ 返回 task_id    │
└────────┬────────┘
       ▼
┌─────────────────┐
│ 计算分片        │
│ chunk_size=5MB  │
└────────┬────────┘
       ▼
┌─────────────────────────────┐
│ 循环上传分片                 │
│ POST /upload/{id}/chunk     │
│ 支持断点续传                 │
└────────┬────────────────────┘
       ▼
┌─────────────────┐
│ POST /complete  │
│ 合并分片        │
│ 生成缩略图      │
└────────┬────────┘
       ▼
┌─────────────────┐
│ 创建 VideoFile  │
└─────────────────┘
```

## 6. 观看码验证流程

```
┌─────────────┐
│ 访客访问首页 │
└──────┬──────┘
       ▼
┌─────────────────┐
│ 检查本地存储    │
│ 是否有有效观看码│
└────────┬────────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
有效     无效/无
   │       │
   │       ▼
   │  ┌─────────────┐
   │  │ 跳转验证页面 │
   │  │ 输入观看码   │
   │  └──────┬──────┘
   │         ▼
   │  ┌─────────────┐
   │  │ POST /verify│
   │  └──────┬──────┘
   │         │
   │    ┌────┴────┐
   │    │         │
   │    ▼         ▼
   │  验证成功   验证失败
   │    │         │
   │    ▼         ▼
   │  存储到     显示错误
   │  localStorage
   │    │
   └────┼─────────┘
        ▼
┌─────────────────┐
│ 显示可访问的    │
│ 分类下的视频    │
└─────────────────┘
```

## 7. 文件约束

| 类型 | 格式 | 大小上限 |
|------|------|----------|
| 视频 | MP4 | 10GB |
| 音频 | MP3/WAV/AAC/FLAC | 1GB |

## 8. 实现任务清单

1. 数据库迁移 - 新增表结构
2. 分类 CRUD API
3. 标签 CRUD API
4. 分片上传服务
5. 观看码管理 API
6. 观看码验证中间件
7. 前端上传组件
8. 前端分类/标签管理页面
9. 前端观看码管理页面
10. 首页分类/标签筛选
