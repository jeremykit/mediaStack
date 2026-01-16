# 第二阶段实现计划

## 概述
基于 `2026-01-14-phase2-design.md` 设计文档，本计划将第二阶段拆分为可独立验证的实现任务。

## 前置依赖
- 第一阶段完成（直播源管理、录制、基础播放）

## 依赖关系图

```
[1. 数据库迁移]
       │
       ├──────────────────┬──────────────────┐
       ▼                  ▼                  ▼
[2. 分类管理 API]   [3. 标签管理 API]   [4. 上传任务模型]
       │                  │                  │
       ├──────────────────┤                  │
       ▼                  ▼                  ▼
[5. VideoFile 扩展]                   [6. 分片上传服务]
       │                                     │
       ├─────────────────────────────────────┤
       ▼                                     ▼
[7. 观看码管理 API]                   [8. 前端上传组件]
       │                                     │
       ▼                                     │
[9. 观看码验证中间件]                        │
       │                                     │
       ├─────────────────────────────────────┤
       ▼                                     ▼
[10. 前端分类管理]  [11. 前端标签管理]  [12. 前端上传页面]
       │                  │                  │
       ├──────────────────┼──────────────────┤
       ▼                  ▼                  ▼
[13. 前端观看码管理]
       │
       ▼
[14. 观看码验证页面]
       │
       ▼
[15. 首页筛选功能]
       │
       ▼
[16. 视频管理扩展]
       │
       ▼
[17. 集成测试]
```

---

## 任务清单

### 1. 数据库迁移
**目标**: 新增第二阶段所需的数据表

**交付物**:
- `backend/app/models/category.py` - Category 模型
- `backend/app/models/tag.py` - Tag 模型
- `backend/app/models/video_tag.py` - VideoTag 关联模型
- `backend/app/models/view_code.py` - ViewCode 模型
- `backend/app/models/view_code_category.py` - ViewCodeCategory 关联模型
- `backend/app/models/upload_task.py` - UploadTask 模型
- 更新 `backend/app/models/__init__.py`

**数据模型**:

| 表名 | 字段 |
|------|------|
| categories | id, name(32), sort_order, created_at |
| tags | id, name(16), created_at |
| video_tags | video_id, tag_id |
| view_codes | id, code(12), is_active, created_at, expires_at |
| view_code_categories | code_id, category_id |
| upload_tasks | id(UUID), filename(256), file_size, chunk_size, total_chunks, uploaded_chunks, status, created_at |

**VideoFile 扩展字段**:
- category_id (INTEGER, 可空)
- file_type (ENUM: video/audio)

**验收标准**:
- [ ] 应用启动时自动创建新表
- [ ] 外键约束正确
- [ ] VideoFile 新字段可空，兼容现有数据

---

### 2. 分类管理 API
**目标**: 实现分类 CRUD

**依赖**: 任务 1

**交付物**:
- `backend/app/schemas/category.py` - 请求/响应模型
- `backend/app/api/categories.py` - 分类路由

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/categories | 获取分类列表（按 sort_order 排序）|
| POST | /api/categories | 创建分类 |
| PUT | /api/categories/{id} | 更新分类 |
| DELETE | /api/categories/{id} | 删除分类 |

**请求/响应模型**:
```python
# 创建/更新请求
class CategoryCreate(BaseModel):
    name: str = Field(max_length=32)
    sort_order: int = 0

# 响应
class CategoryResponse(BaseModel):
    id: int
    name: str
    sort_order: int
    created_at: datetime
    video_count: int  # 该分类下的视频数量
```

**验收标准**:
- [ ] CRUD 操作正常
- [ ] 分类名称唯一性校验
- [ ] 删除分类时检查是否有关联视频
- [ ] 返回每个分类的视频数量

---

### 3. 标签管理 API
**目标**: 实现标签 CRUD

**依赖**: 任务 1

**交付物**:
- `backend/app/schemas/tag.py` - 请求/响应模型
- `backend/app/api/tags.py` - 标签路由

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tags | 获取标签列表 |
| POST | /api/tags | 创建标签 |
| DELETE | /api/tags/{id} | 删除标签 |

**请求/响应模型**:
```python
# 创建请求
class TagCreate(BaseModel):
    name: str = Field(max_length=16)

# 响应
class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    video_count: int  # 使用该标签的视频数量
```

**验收标准**:
- [ ] CRUD 操作正常
- [ ] 标签名称唯一性校验
- [ ] 删除标签时自动清理关联关系
- [ ] 返回每个标签的使用次数

---

### 4. 上传任务模型
**目标**: 实现上传任务数据模型

**依赖**: 任务 1

**交付物**:
- `backend/app/schemas/upload.py` - 请求/响应模型

**状态枚举**:
```python
class UploadStatus(str, Enum):
    uploading = "uploading"
    completed = "completed"
    failed = "failed"
```

**验收标准**:
- [ ] 模型字段完整
- [ ] UUID 主键生成正确

---

### 5. VideoFile 扩展
**目标**: 扩展 VideoFile 模型支持分类和标签

**依赖**: 任务 1, 2, 3

**交付物**:
- 更新 `backend/app/models/video.py`
- 更新 `backend/app/schemas/video.py`
- 更新 `backend/app/api/videos.py`

**新增 API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| PUT | /api/videos/{id}/category | 设置视频分类 |
| PUT | /api/videos/{id}/tags | 设置视频标签 |

**请求模型**:
```python
class SetCategoryRequest(BaseModel):
    category_id: Optional[int] = None

class SetTagsRequest(BaseModel):
    tag_ids: List[int]
```

**验收标准**:
- [ ] 视频可设置分类
- [ ] 视频可设置多个标签
- [ ] 视频列表返回分类和标签信息
- [ ] 现有视频数据兼容（category_id 和 tags 为空）

---

### 6. 分片上传服务
**目标**: 实现大文件分片上传

**依赖**: 任务 4

**交付物**:
- `backend/app/services/uploader.py` - 上传服务
- `backend/app/api/upload.py` - 上传路由

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload/init | 初始化上传任务 |
| POST | /api/upload/{task_id}/chunk | 上传分片 |
| POST | /api/upload/{task_id}/complete | 完成上传 |
| GET | /api/upload/{task_id}/status | 查询上传状态 |
| DELETE | /api/upload/{task_id} | 取消上传 |

**初始化请求**:
```python
class UploadInitRequest(BaseModel):
    filename: str
    file_size: int
    chunk_size: int = 5 * 1024 * 1024  # 默认 5MB
```

**初始化响应**:
```python
class UploadInitResponse(BaseModel):
    task_id: str
    chunk_size: int
    total_chunks: int
```

**分片上传请求**:
- Content-Type: multipart/form-data
- chunk_index: int (0-based)
- chunk: File

**上传流程**:
1. 前端调用 `/init` 获取 task_id
2. 前端计算分片，循环调用 `/chunk` 上传
3. 后端将分片存储到临时目录 `{storage_path}/temp/{task_id}/`
4. 前端调用 `/complete` 触发合并
5. 后端合并分片，生成缩略图，创建 VideoFile 记录
6. 清理临时文件

**文件约束**:
| 类型 | 格式 | 大小上限 |
|------|------|----------|
| 视频 | MP4 | 10GB |
| 音频 | MP3/WAV/AAC/FLAC | 1GB |

**验收标准**:
- [ ] 初始化返回正确的分片数
- [ ] 分片上传支持乱序
- [ ] 断点续传（查询已上传分片）
- [ ] 合并后文件完整
- [ ] 自动生成缩略图（视频）
- [ ] 自动检测文件类型（video/audio）
- [ ] 超时任务自动清理（24小时）

---

### 7. 观看码管理 API
**目标**: 实现观看码 CRUD 和验证

**依赖**: 任务 1, 2

**交付物**:
- `backend/app/schemas/view_code.py` - 请求/响应模型
- `backend/app/api/view_codes.py` - 观看码路由

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/view-codes | 获取观看码列表 |
| POST | /api/view-codes | 创建观看码 |
| PUT | /api/view-codes/{id} | 更新观看码 |
| DELETE | /api/view-codes/{id} | 删除观看码 |
| POST | /api/view-codes/verify | 验证观看码 |

**创建请求**:
```python
class ViewCodeCreate(BaseModel):
    code: str = Field(min_length=6, max_length=12, pattern="^[a-zA-Z0-9]+$")
    is_active: bool = True
    expires_at: Optional[datetime] = None
    category_ids: List[int] = []
```

**验证请求/响应**:
```python
class ViewCodeVerifyRequest(BaseModel):
    code: str

class ViewCodeVerifyResponse(BaseModel):
    valid: bool
    category_ids: List[int] = []  # 可访问的分类 ID
    expires_at: Optional[datetime] = None
```

**验收标准**:
- [ ] CRUD 操作正常
- [ ] 观看码格式校验（6-12位字母数字）
- [ ] 观看码唯一性校验
- [ ] 验证时检查是否启用、是否过期
- [ ] 返回可访问的分类列表

---

### 8. 前端上传组件
**目标**: 实现拖拽上传组件

**依赖**: 任务 6

**交付物**:
- `frontend/src/components/ChunkUploader.vue` - 分片上传组件
- `frontend/src/api/upload.ts` - 上传 API 调用
- `frontend/src/utils/file.ts` - 文件处理工具

**组件功能**:
- 拖拽上传区域
- 文件类型校验（MP4/MP3/WAV/AAC/FLAC）
- 文件大小校验
- 上传进度显示（总进度 + 当前分片）
- 暂停/继续上传
- 取消上传
- 上传完成回调

**验收标准**:
- [ ] 拖拽上传正常
- [ ] 点击选择文件正常
- [ ] 进度条准确显示
- [ ] 暂停/继续功能正常
- [ ] 取消上传清理服务端临时文件
- [ ] 上传完成显示成功提示

---

### 9. 观看码验证中间件
**目标**: 实现访客访问控制

**依赖**: 任务 7

**交付物**:
- `backend/app/api/deps.py` - 新增 `get_view_code_categories` 依赖
- 更新 `backend/app/api/videos.py` - 首页视频列表增加分类过滤

**验证逻辑**:
1. 从请求头 `X-View-Code` 获取观看码
2. 验证观看码有效性
3. 返回可访问的分类 ID 列表
4. 视频列表 API 根据分类过滤

**验收标准**:
- [ ] 无观看码时返回空列表或公开视频
- [ ] 有效观看码返回对应分类的视频
- [ ] 过期观看码返回 401
- [ ] 禁用观看码返回 401

---

### 10. 前端分类管理
**目标**: 实现分类管理页面

**依赖**: 任务 2

**交付物**:
- `frontend/src/views/admin/Categories.vue` - 分类管理页
- `frontend/src/api/categories.ts` - API 调用

**页面功能**:
- 分类列表（表格形式）
- 新增分类（对话框）
- 编辑分类（对话框）
- 删除分类（确认对话框）
- 拖拽排序

**验收标准**:
- [ ] 列表展示分类
- [ ] 新增/编辑表单验证
- [ ] 删除确认对话框
- [ ] 拖拽排序更新 sort_order
- [ ] 显示每个分类的视频数量

---

### 11. 前端标签管理
**目标**: 实现标签管理页面

**依赖**: 任务 3

**交付物**:
- `frontend/src/views/admin/Tags.vue` - 标签管理页
- `frontend/src/api/tags.ts` - API 调用

**页面功能**:
- 标签列表（标签云或表格）
- 新增标签
- 删除标签

**验收标准**:
- [ ] 列表展示标签
- [ ] 新增标签
- [ ] 删除标签（确认对话框）
- [ ] 显示每个标签的使用次数

---

### 12. 前端上传页面
**目标**: 实现文件上传页面

**依赖**: 任务 8

**交付物**:
- `frontend/src/views/admin/Upload.vue` - 上传页面

**页面功能**:
- 使用 ChunkUploader 组件
- 上传完成后可设置标题、分类、标签
- 上传历史列表

**验收标准**:
- [ ] 上传页面正常显示
- [ ] 上传完成后可编辑元数据
- [ ] 支持批量上传（队列）

---

### 13. 前端观看码管理
**目标**: 实现观看码管理页面

**依赖**: 任务 7, 10

**交付物**:
- `frontend/src/views/admin/ViewCodes.vue` - 观看码管理页
- `frontend/src/api/viewCodes.ts` - API 调用

**页面功能**:
- 观看码列表
- 新增观看码（可选择关联分类）
- 编辑观看码
- 删除观看码
- 启用/禁用开关
- 复制观看码到剪贴板

**验收标准**:
- [ ] 列表展示观看码
- [ ] 新增时可选择多个分类
- [ ] 显示过期状态
- [ ] 启用/禁用开关
- [ ] 一键复制功能

---

### 14. 观看码验证页面
**目标**: 实现访客验证页面

**依赖**: 任务 9

**交付物**:
- `frontend/src/views/Verify.vue` - 验证页面
- `frontend/src/stores/viewCode.ts` - 观看码状态管理
- 更新 `frontend/src/router/index.ts` - 路由守卫

**页面功能**:
- 观看码输入框
- 验证按钮
- 错误提示
- 验证成功后存储到 localStorage
- 路由守卫检查观看码

**验证流程**:
1. 访客访问首页
2. 路由守卫检查 localStorage 中的观看码
3. 无有效观看码则跳转到 `/verify`
4. 输入观看码，调用验证 API
5. 验证成功，存储观看码和可访问分类到 localStorage
6. 跳转回首页

**验收标准**:
- [ ] 验证页面正常显示
- [ ] 验证成功跳转首页
- [ ] 验证失败显示错误
- [ ] localStorage 正确存储
- [ ] 路由守卫正常工作

---

### 15. 首页筛选功能
**目标**: 首页增加分类和标签筛选

**依赖**: 任务 5, 9, 14

**交付物**:
- 更新 `frontend/src/views/Home.vue`
- 更新 `backend/app/api/videos.py` - 增加筛选参数

**API 扩展**:
```
GET /api/videos?category_id=1&tag_ids=1,2,3&search=keyword
```

**页面功能**:
- 分类筛选（下拉或标签页）
- 标签筛选（多选）
- 搜索框
- 筛选条件组合

**验收标准**:
- [ ] 分类筛选正常
- [ ] 标签筛选正常（多选）
- [ ] 搜索功能正常
- [ ] 筛选条件可组合
- [ ] 根据观看码限制可见分类

---

### 16. 视频管理扩展
**目标**: 视频管理页面增加分类/标签编辑

**依赖**: 任务 5, 10, 11

**交付物**:
- 更新 `frontend/src/views/admin/Videos.vue`

**页面功能**:
- 视频列表显示分类和标签
- 编辑视频时可设置分类
- 编辑视频时可设置标签（多选）
- 批量设置分类/标签

**验收标准**:
- [ ] 列表显示分类和标签
- [ ] 编辑分类正常
- [ ] 编辑标签正常
- [ ] 批量操作正常

---

### 17. 集成测试
**目标**: 端到端功能验证

**依赖**: 任务 1-16

**测试场景**:
1. 分类管理（CRUD + 排序）
2. 标签管理（CRUD）
3. 文件上传（小文件 + 大文件分片）
4. 观看码管理（CRUD + 分类关联）
5. 观看码验证流程
6. 首页筛选功能
7. 视频分类/标签编辑

**验收标准**:
- [ ] 所有场景通过
- [ ] 无明显 bug
- [ ] 性能可接受

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 大文件上传中断 | 用户体验差 | 分片上传 + 断点续传 |
| 分片合并内存占用 | 服务器压力 | 流式合并，不一次性加载 |
| 观看码泄露 | 内容被盗看 | 支持过期时间 + 禁用功能 |
| 临时文件堆积 | 磁盘占满 | 定时清理超时任务 |

---

## 技术决策记录

### TD-005: 分片上传方案
**决策**: 自实现分片上传，不使用第三方库
**原因**: 需求简单，避免引入额外依赖
**替代方案**: tus-py-client（协议复杂）、resumable.js（前端库）

### TD-006: 观看码存储
**决策**: 明文存储观看码
**原因**: 观看码需要展示给管理员，且安全要求不高
**替代方案**: 哈希存储（无法展示原始码）

### TD-007: 分类与观看码关系
**决策**: 多对多关系，一个观看码可访问多个分类
**原因**: 灵活性高，支持不同访问级别
**替代方案**: 一对多（限制性强）

### TD-008: 文件类型检测
**决策**: 基于文件扩展名 + MIME 类型双重校验
**原因**: 简单可靠
**替代方案**: 文件头魔数检测（实现复杂）

---

## 路由配置更新

```typescript
// frontend/src/router/index.ts 新增路由
{
  path: '/verify',
  name: 'Verify',
  component: () => import('@/views/Verify.vue'),
  meta: { requiresAuth: false }
},
{
  path: '/admin/upload',
  name: 'AdminUpload',
  component: () => import('@/views/admin/Upload.vue'),
  meta: { requiresAuth: true }
},
{
  path: '/admin/categories',
  name: 'AdminCategories',
  component: () => import('@/views/admin/Categories.vue'),
  meta: { requiresAuth: true }
},
{
  path: '/admin/tags',
  name: 'AdminTags',
  component: () => import('@/views/admin/Tags.vue'),
  meta: { requiresAuth: true }
},
{
  path: '/admin/view-codes',
  name: 'AdminViewCodes',
  component: () => import('@/views/admin/ViewCodes.vue'),
  meta: { requiresAuth: true }
}
```

---

## 后端路由注册

```python
# backend/app/main.py 新增路由
from app.api import categories, tags, upload, view_codes

app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(view_codes.router, prefix="/api/view-codes", tags=["view-codes"])
```
