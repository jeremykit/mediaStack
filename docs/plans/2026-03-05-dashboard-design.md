# Dashboard 页面设计文档

## 项目概述

为 MediaStack 管理后台设计并实现一个综合概览 Dashboard 页面，提供系统监控和内容管理的统一视图。

## 需求总结

### 用户场景
- **目标用户**: 管理员
- **使用场景**: 日常运维和内容管理的首页入口
- **核心价值**: 一屏掌握系统状态、录制进度、内容统计

### 功能需求

Dashboard 需要展示以下 8 个核心信息卡片：

1. **实时录制状态** - 当前正在录制的任务列表（源名称、录制时长）
2. **待处理视频** - 待审核视频数量 + 快速跳转
3. **系统资源概览** - CPU/内存/磁盘使用率精简展示
4. **直播源状态** - 总数/在线/离线/录制中统计
5. **近期录制活动** - 最近完成的录制任务列表
6. **定时计划概览** - 今日计划数量、即将执行的下一个计划
7. **存储统计** - 文件总数、存储占用、按分类统计
8. **访问/下载量统计** - 今天/本周/本月维度，区分视频/音频

### 非功能需求

- **性能**: 页面加载时间 < 2s，通过合并接口减少请求次数
- **刷新策略**: 实时数据自动刷新（30s），统计数据手动刷新
- **响应式**: 适配桌面和移动端
- **一致性**: 与现有 admin 页面风格保持一致

## 架构设计

### 路由设计

```
/admin/dashboard - Dashboard 页面（管理后台默认首页）
```

- 访问 `/admin` 时自动重定向到 `/admin/dashboard`
- 侧边栏新增"仪表盘"菜单项，置顶显示

### 布局设计

**响应式网格布局（卡片式）**

```
桌面端 (>768px):
┌─────────────────────────────────────────┐
│ [实时录制 2x1]  [待处理 1x1] [系统 1x1] │
│ [源状态 1x1] [计划 1x1] [存储 1x1]      │
│ [近期活动 2x1]  [访问统计 2x1]         │
└─────────────────────────────────────────┘

移动端 (<768px):
单列堆叠，每个卡片占满宽度
```

## API 设计

### 设计原则

- **合并请求**: 将相关数据合并到 3 个接口，减少请求次数
- **一次返回**: 统计接口一次返回三个时间维度的数据
- **性能优化**: 后端预聚合数据，减少前端计算

### 接口定义

#### 1. 实时概览接口

```http
GET /admin/dashboard/overview
```

**返回结构:**
```json
{
  "recording_tasks": [
    {
      "id": 1,
      "source_name": "CCTV-1",
      "started_at": "2026-03-05T08:00:00Z",
      "duration": 900
    }
  ],
  "recording_count": 3,
  "pending_video_count": 12,
  "sources": {
    "total": 20,
    "online": 15,
    "offline": 5,
    "recording": 3
  },
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 62.8,
    "disk_percent": 73.5
  }
}
```

**刷新策略**: 自动刷新，间隔 30 秒

#### 2. 统计数据接口

```http
GET /admin/dashboard/statistics
```

**返回结构:**
```json
{
  "storage": {
    "total_files": 1523,
    "total_size": 524288000000,
    "by_category": [
      { "name": "新闻", "count": 450, "size": 150000000000 },
      { "name": "综艺", "count": 320, "size": 120000000000 }
    ]
  },
  "traffic_by_period": [
    {
      "period": "today",
      "video_views": 1250,
      "audio_views": 340,
      "video_downloads": 89,
      "audio_downloads": 23
    },
    {
      "period": "week",
      "video_views": 8920,
      "audio_views": 2340,
      "video_downloads": 567,
      "audio_downloads": 145
    },
    {
      "period": "month",
      "video_views": 35600,
      "audio_views": 9800,
      "video_downloads": 2340,
      "audio_downloads": 678
    }
  ]
}
```

**刷新策略**: 手动刷新

#### 3. 近期活动接口

```http
GET /admin/dashboard/activity
```

**返回结构:**
```json
{
  "recent_tasks": [
    {
      "id": 45,
      "source_name": "CCTV-1",
      "status": "completed",
      "completed_at": "2026-03-05T07:30:00Z",
      "duration": 3600,
      "file_size": 2048000000
    }
  ],
  "upcoming_schedules": [
    {
      "id": 12,
      "source_name": "CCTV-2",
      "next_run": "2026-03-05T09:00:00Z",
      "cron_expression": "0 9 * * *"
    }
  ]
}
```

**刷新策略**: 手动刷新

### 后端实现要点

#### 新增数据表

```sql
-- 下载记录表
CREATE TABLE downloads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id INTEGER NOT NULL,
  downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (video_id) REFERENCES videos(id)
);

-- 为查询性能添加索引
CREATE INDEX idx_downloads_video_id ON downloads(video_id);
CREATE INDEX idx_downloads_downloaded_at ON downloads(downloaded_at);
```

#### 新增 API 路由

```python
# app/api/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db

router = APIRouter(prefix="/admin/dashboard", tags=["dashboard"])

@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    # 实现概览数据聚合
    pass

@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    # 实现统计数据聚合
    pass

@router.get("/activity")
async def get_activity(db: AsyncSession = Depends(get_db)):
    # 实现活动数据查询
    pass
```

#### 下载记录 API

```python
# app/api/videos.py 新增
@router.post("/{video_id}/download")
async def record_download(video_id: int, db: AsyncSession = Depends(get_db)):
    # 记录下载行为
    pass
```

## 前端设计

### 组件结构

```
views/admin/Dashboard.vue          # 主页面
components/dashboard/
  ├── RecordingCard.vue            # 实时录制卡片
  ├── PendingVideoCard.vue         # 待处理视频卡片
  ├── SystemResourceCard.vue       # 系统资源卡片
  ├── SourceStatusCard.vue         # 直播源状态卡片
  ├── RecentActivityCard.vue       # 近期活动卡片
  ├── ScheduleCard.vue             # 定时计划卡片
  ├── StorageCard.vue              # 存储统计卡片
  └── TrafficCard.vue              # 访问/下载量卡片
```

### 状态管理

```typescript
// stores/dashboard.ts
export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    overview: null,
    statistics: null,
    activity: null,
    loading: {
      overview: false,
      statistics: false,
      activity: false
    }
  }),
  actions: {
    async fetchOverview() { /* ... */ },
    async fetchStatistics() { /* ... */ },
    async fetchActivity() { /* ... */ },
    async refreshAll() { /* ... */ }
  }
})
```

### API 客户端

```typescript
// api/dashboard.ts
export interface DashboardOverview {
  recording_tasks: RecordingTask[]
  recording_count: number
  pending_video_count: number
  sources: SourceStats
  system: SystemStats
}

export interface DashboardStatistics {
  storage: StorageStats
  traffic_by_period: TrafficStats[]
}

export interface DashboardActivity {
  recent_tasks: Task[]
  upcoming_schedules: Schedule[]
}

export const dashboardApi = {
  getOverview: () => api.get<DashboardOverview>('/admin/dashboard/overview'),
  getStatistics: () => api.get<DashboardStatistics>('/admin/dashboard/statistics'),
  getActivity: () => api.get<DashboardActivity>('/admin/dashboard/activity')
}
```

### UI 设计规范

**卡片样式:**
- 背景: `rgba(15, 20, 35, 0.6)` + 毛玻璃效果
- 边框: `1px solid rgba(255, 255, 255, 0.05)`
- 圆角: `12px`
- 阴影: `0 4px 24px rgba(0, 0, 0, 0.3)`

**数值展示:**
- 大数字: `32px`, 渐变色 `#E94560 → #8B5CF6`
- 标签: `14px`, `rgba(255, 255, 255, 0.6)`
- 图标: `24px`, 与品牌色一致

**交互反馈:**
- 卡片 hover: 边框高亮 + 轻微上浮
- 加载状态: 骨架屏
- 错误状态: 显示重试按钮

## 数据流设计

### 页面加载流程

```
1. 用户访问 /admin/dashboard
2. 并行请求 3 个 API:
   - fetchOverview()
   - fetchStatistics()
   - fetchActivity()
3. 各卡片独立渲染，失败不影响其他卡片
4. overview 数据启动自动刷新定时器（30s）
```

### 刷新机制

**自动刷新 (overview):**
```typescript
let refreshTimer: number | null = null

onMounted(() => {
  fetchOverview()
  refreshTimer = setInterval(fetchOverview, 30000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
```

**手动刷新:**
- 页面右上角全局刷新按钮
- 单个卡片刷新按钮（可选）

## 实施计划

### 阶段 1: 后端 API 实现
1. 创建 `downloads` 表和迁移脚本
2. 实现 3 个 Dashboard API 接口
3. 实现下载记录 API
4. 编写单元测试

### 阶段 2: 前端组件实现
1. 创建 Dashboard 页面和路由
2. 实现 8 个卡片组件
3. 实现状态管理和 API 调用
4. 实现刷新机制

### 阶段 3: 集成测试
1. 前后端联调
2. 性能测试（页面加载时间）
3. 响应式测试（移动端适配）
4. 边界情况测试（空数据、错误处理）

### 阶段 4: 优化与部署
1. 代码审查
2. 文档更新
3. 部署到生产环境

## 技术风险与应对

### 风险 1: 统计查询性能
- **风险**: 大数据量下统计查询可能较慢
- **应对**:
  - 添加数据库索引
  - 考虑引入缓存（Redis）
  - 异步后台任务预计算统计数据

### 风险 2: 前端请求并发
- **风险**: 3 个 API 并发可能导致服务器压力
- **应对**:
  - 后端实现请求限流
  - 前端实现请求队列
  - 考虑使用 HTTP/2 多路复用

### 风险 3: 实时数据一致性
- **风险**: 自动刷新可能导致数据闪烁
- **应对**:
  - 使用平滑过渡动画
  - 仅更新变化的数据
  - 提供"暂停刷新"选项

## 后续扩展

- **图表可视化**: 引入 ECharts 展示趋势图
- **自定义布局**: 允许用户拖拽调整卡片位置
- **告警通知**: 系统资源超阈值时弹窗提醒
- **导出报表**: 支持导出 PDF/Excel 格式的统计报表
- **WebSocket 实时推送**: 替代轮询，实现真正的实时更新

## 总结

Dashboard 页面通过 3 个优化的 API 接口，以卡片式布局展示系统的核心指标和运营数据，为管理员提供高效的一站式管理入口。设计注重性能优化和用户体验，与现有系统风格保持一致。
