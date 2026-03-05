# Dashboard 页面实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 MediaStack 管理后台的 Dashboard 综合概览页面，提供系统监控和内容管理的统一视图

**Architecture:** 后端新增 3 个聚合 API 接口（overview/statistics/activity），前端采用卡片式网格布局展示 8 个核心指标卡片，实时数据自动刷新，统计数据手动刷新

**Tech Stack:** FastAPI, SQLAlchemy (async), Vue 3, TypeScript, Element Plus

---

## 实施阶段概览

### 阶段 1: 后端基础设施 (Tasks 1-5)
- 创建下载记录模型
- 实现 Dashboard API schemas
- 实现 3 个 Dashboard API 接口
- 实现下载记录 API
- 后端单元测试

### 阶段 2: 前端基础设施 (Tasks 6-8)
- 创建 Dashboard API 客户端
- 创建 Dashboard 状态管理
- 创建 Dashboard 页面和路由

### 阶段 3: 前端卡片组件 (Tasks 9-16)
- 实现 8 个卡片组件
- 实现刷新机制

### 阶段 4: 集成与测试 (Tasks 17-18)
- 前后端集成测试
- 响应式测试和优化

---

## Task 1: 创建下载记录数据模型

**Files:**
- Create: `backend/app/models/download.py`
- Modify: `backend/app/models/__init__.py`

**Step 1: 创建 Download 模型**

```python
# backend/app/models/download.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Download(Base):
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    downloaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
```

**Step 2: 导入模型**

在 `backend/app/models/__init__.py` 末尾添加：
```python
from app.models.download import Download
```

**Step 3: 创建迁移**

Run: `cd backend && alembic revision --autogenerate -m "add downloads table"`

**Step 4: 提交**

```bash
git add backend/app/models/download.py backend/app/models/__init__.py backend/alembic/versions/
git commit -m "feat(backend): add Download model and migration"
```

---

## Task 2: 实现 Dashboard Schemas

**Files:**
- Create: `backend/app/schemas/dashboard.py`

**Step 1: 创建完整的 schemas 文件**

创建 `backend/app/schemas/dashboard.py` 包含所有必要的 Pydantic 模型（RecordingTaskInfo, SourceStats, SystemStats, DashboardOverview, StorageStats, TrafficStats, DashboardStatistics, RecentTaskInfo, UpcomingScheduleInfo, DashboardActivity）

参考设计文档中的 API 返回结构定义所有字段和类型。

**Step 2: 提交**

```bash
git add backend/app/schemas/dashboard.py
git commit -m "feat(backend): add Dashboard schemas"
```

---

## Task 3: 实现 Dashboard API - Overview 接口

**Files:**
- Create: `backend/app/api/dashboard.py`
- Modify: `backend/app/main.py`

**Step 1: 创建 dashboard.py 并实现 get_overview**

实现逻辑：
1. 查询 status='recording' 的 tasks
2. 统计 status='pending' 的 videos
3. 聚合 sources 统计（total, online, offline, recording）
4. 调用现有的 system status API

**Step 2: 在 main.py 中注册路由**

```python
from app.api import dashboard
app.include_router(dashboard.router)
```

**Step 3: 测试接口**

Run: `curl http://localhost:8000/admin/dashboard/overview`

**Step 4: 提交**

```bash
git add backend/app/api/dashboard.py backend/app/main.py
git commit -m "feat(backend): implement dashboard overview API"
```

---

## Task 4: 实现 Dashboard API - Statistics 和 Activity 接口

**Files:**
- Modify: `backend/app/api/dashboard.py`

**Step 1: 实现 get_statistics**

实现逻辑：
1. 查询所有 videos 聚合存储统计
2. 按 category 分组统计
3. 查询 downloads 表按时间范围聚合（today/week/month）
4. 聚合 view_count 按时间范围和 file_type

**Step 2: 实现 get_activity**

实现逻辑：
1. 查询最近 10 条 completed 的 tasks
2. 查询 schedules 并计算 next_run_time

**Step 3: 测试接口**

Run: 
```bash
curl http://localhost:8000/admin/dashboard/statistics
curl http://localhost:8000/admin/dashboard/activity
```

**Step 4: 提交**

```bash
git add backend/app/api/dashboard.py
git commit -m "feat(backend): implement dashboard statistics and activity APIs"
```

---

## Task 5: 实现下载记录 API

**Files:**
- Modify: `backend/app/api/videos.py`

**Step 1: 添加 record_download 端点**

```python
@router.post("/{video_id}/download")
async def record_download(video_id: int, db: AsyncSession = Depends(get_db)):
    # 验证 video 存在
    # 创建 Download 记录
    # 返回成功响应
    pass
```

**Step 2: 测试**

Run: `curl -X POST http://localhost:8000/videos/1/download`

**Step 3: 提交**

```bash
git add backend/app/api/videos.py
git commit -m "feat(backend): add download recording API"
```

---

## Task 6: 创建前端 Dashboard API 客户端

**Files:**
- Create: `frontend/src/api/dashboard.ts`

**Step 1: 定义 TypeScript 接口和 API 函数**

参考设计文档定义所有接口类型（DashboardOverview, DashboardStatistics, DashboardActivity）和 API 调用函数。

**Step 2: 提交**

```bash
git add frontend/src/api/dashboard.ts
git commit -m "feat(frontend): add Dashboard API client"
```

---

## Task 7: 创建 Dashboard 状态管理

**Files:**
- Create: `frontend/src/stores/dashboard.ts`

**Step 1: 创建 Pinia store**

实现 state（overview, statistics, activity, loading）和 actions（fetchOverview, fetchStatistics, fetchActivity, refreshAll）。

**Step 2: 提交**

```bash
git add frontend/src/stores/dashboard.ts
git commit -m "feat(frontend): add Dashboard store"
```

---

## Task 8: 创建 Dashboard 页面和路由

**Files:**
- Create: `frontend/src/views/admin/Dashboard.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/views/admin/Layout.vue`

**Step 1: 创建 Dashboard.vue 基础结构**

包含网格布局容器和全局刷新按钮。

**Step 2: 添加路由**

在 `/admin` children 中添加 `{ path: 'dashboard', name: 'admin-dashboard', component: () => import('../views/admin/Dashboard.vue') }`，并设置为默认子路由。

**Step 3: 在 Layout.vue 侧边栏添加菜单项**

在 recordingMenuItems 之前添加 Dashboard 菜单项。

**Step 4: 提交**

```bash
git add frontend/src/views/admin/Dashboard.vue frontend/src/router/index.ts frontend/src/views/admin/Layout.vue
git commit -m "feat(frontend): add Dashboard page and routing"
```

---

## Task 9-16: 实现 8 个卡片组件

**Files:**
- Create: `frontend/src/components/dashboard/RecordingCard.vue`
- Create: `frontend/src/components/dashboard/PendingVideoCard.vue`
- Create: `frontend/src/components/dashboard/SystemResourceCard.vue`
- Create: `frontend/src/components/dashboard/SourceStatusCard.vue`
- Create: `frontend/src/components/dashboard/RecentActivityCard.vue`
- Create: `frontend/src/components/dashboard/ScheduleCard.vue`
- Create: `frontend/src/components/dashboard/StorageCard.vue`
- Create: `frontend/src/components/dashboard/TrafficCard.vue`
- Modify: `frontend/src/views/admin/Dashboard.vue`

**每个卡片的实现步骤：**

1. 创建组件文件，定义 props 和基础结构
2. 实现数据展示逻辑
3. 添加样式（与现有 admin 风格一致）
4. 在 Dashboard.vue 中导入并使用
5. 提交

**Step 1-8: 逐个实现卡片**

每个卡片一个 commit：
```bash
git add frontend/src/components/dashboard/RecordingCard.vue frontend/src/views/admin/Dashboard.vue
git commit -m "feat(frontend): add Recording status card"
```

---

## Task 17: 实现自动刷新机制

**Files:**
- Modify: `frontend/src/views/admin/Dashboard.vue`

**Step 1: 添加自动刷新逻辑**

在 Dashboard.vue 中：
- onMounted 时启动 overview 自动刷新定时器（30s）
- onUnmounted 时清理定时器
- 实现全局手动刷新按钮

**Step 2: 测试刷新**

验证自动刷新和手动刷新都正常工作。

**Step 3: 提交**

```bash
git add frontend/src/views/admin/Dashboard.vue
git commit -m "feat(frontend): implement auto-refresh mechanism"
```

---

## Task 18: 集成测试和优化

**Step 1: 运行后端迁移**

Run: `cd backend && alembic upgrade head`

**Step 2: 启动后端服务**

Run: `cd backend && uvicorn app.main:app --reload`

**Step 3: 启动前端服务**

Run: `cd frontend && npm run dev`

**Step 4: 手动测试**

- 访问 `/admin/dashboard`
- 验证所有卡片正常加载
- 验证自动刷新工作正常
- 验证手动刷新按钮
- 测试移动端响应式

**Step 5: 修复发现的问题**

根据测试结果修复 bug。

**Step 6: 最终提交**

```bash
git add .
git commit -m "test: Dashboard integration testing and fixes"
```

---

## 验收标准

- [ ] 后端 3 个 API 接口正常返回数据
- [ ] 下载记录功能正常工作
- [ ] Dashboard 页面加载时间 < 2s
- [ ] 所有 8 个卡片正常展示
- [ ] 自动刷新（30s）正常工作
- [ ] 手动刷新按钮正常工作
- [ ] 移动端响应式布局正常
- [ ] 样式与现有 admin 页面一致
- [ ] 无 console 错误
- [ ] 代码已提交到 git

---

## 注意事项

1. **YAGNI**: 只实现设计文档中定义的功能，不添加额外特性
2. **DRY**: 复用现有组件和工具函数（如 formatSize, formatDuration）
3. **TDD**: 后端 API 先写测试再实现（可选，时间允许的情况下）
4. **频繁提交**: 每完成一个小功能就提交
5. **错误处理**: 所有 API 调用都要有 try-catch
6. **加载状态**: 所有异步操作都要显示 loading 状态
7. **空数据处理**: 考虑数据为空时的展示

