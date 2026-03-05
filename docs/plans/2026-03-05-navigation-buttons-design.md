# 导航按钮功能设计文档

**日期：** 2026-03-05
**状态：** 已批准

---

## 一、需求概述

在 MediaStack 系统中添加导航按钮，提升用户体验和页面间跳转便利性：

1. **首页右上角**：添加登录/管理后台/登出按钮
2. **登录页面**：添加返回首页按钮
3. **管理后台**：添加跳转首页按钮

所有功能需适配移动端显示。

---

## 二、组件架构

```
frontend/src/
├── components/
│   └── HeaderNav.vue          # 新建：首页右上角导航组件
├── views/
│   ├── Home.vue               # 修改：引入 HeaderNav
│   ├── Login.vue              # 修改：添加返回首页按钮
│   └── admin/
│       └── Layout.vue         # 修改：header-right 添加首页按钮
```

---

## 三、组件设计

### 3.1 HeaderNav.vue（首页导航组件）

**功能：**
- 未登录：显示"登录"按钮
- 已登录：显示"进入管理后台" + "登出"按钮

**模板结构：**
```vue
<div class="header-nav">
  <router-link v-if="!authStore.isLoggedIn" to="/login" class="nav-btn login-btn">
    登录
  </router-link>
  <template v-else>
    <router-link to="/admin/sources" class="nav-btn admin-btn">
      进入管理后台
    </router-link>
    <button @click="handleLogout" class="nav-btn logout-btn">
      登出
    </button>
  </template>
</div>
```

**响应式样式：**
- 桌面端（> 768px）：按钮水平排列，高度 40px
- 移动端（≤ 768px）：按钮高度 36px，保持清晰可读

### 3.2 Home.vue 修改

**改动点：**
1. 引入 `HeaderNav` 组件
2. 在 `hero-content` 内顶部添加导航
3. 调整 `brand-area` 和 `search-area` 的上边距

**位置：**
```vue
<div class="hero-content">
  <HeaderNav />
  <div class="brand-area">...</div>
  <div class="search-area">...</div>
</div>
```

### 3.3 Login.vue 修改

**改动点：**
在登录按钮下方添加返回首页按钮

**模板结构：**
```vue
<el-button class="login-button" @click="handleLogin">
  登录
</el-button>
<router-link to="/" class="back-to-home-btn">
  返回首页
</router-link>
```

**样式：** outline 边框样式，次要按钮视觉

### 3.4 Layout.vue 修改

**改动点：**
在 `header-right` 区域添加首页跳转按钮

**模板结构：**
```vue
<div class="header-right">
  <router-link to="/" class="home-link-btn">
    <svg><!-- home icon --></svg>
    <span class="home-text">首页</span>
  </router-link>
  <SystemStatus />
</div>
```

**响应式样式：**
- 桌面端：显示图标 + 文字
- 移动端：只显示图标，使用 title 属性提示

---

## 四、样式规范

| 位置 | 桌面端高度 | 移动端高度 | 颜色 |
|------|-----------|-----------|------|
| 首页导航-登录 | 40px | 36px | 渐变粉色 |
| 首页导航-后台 | 40px | 36px | 半透明白色 |
| 首页导航-登出 | 40px | 36px | 边框样式 |
| 登录页返回 | 48px | 44px | 边框样式 |
| 后台首页 | 36px | 32px | 半透明白色 |

**响应式断点：**
- `@media (max-width: 768px)` - 移动端样式生效

---

## 五、交互流程

```
┌─────────────────────────────────────────────────────────────┐
│                        首页 (/)                             │
│  ┌─────────────┐                                           │
│  │ [登录]      │  → 未登录状态，点击跳转 /login              │
│  └─────────────┘                                           │
│                                                             │
│  ┌──────────────┬──────────────┐                           │
│  │ 进入管理后台  │   [登出]      │  → 已登录状态               │
│  └──────────────┴──────────────┘                           │
│       ↓ 跳转 /admin      ↓ 清除 token                        │
└─────────────────────────────────────────────────────────────┘
                              ↓ 登录成功
┌─────────────────────────────────────────────────────────────┐
│                      管理后台 (/admin/*)                     │
│  ┌──────────────┐  ┌─────────────┐                         │
│  │ [首页]       │  │ [系统状态]   │  → 右上角导航            │
│  └──────────────┘  └─────────────┘                         │
│       ↓ 跳转 /                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓ 点击返回
┌─────────────────────────────────────────────────────────────┐
│                       登录页 (/login)                        │
│  ┌──────────────┐                                           │
│  │   [登录]     │                                           │
│  └──────────────┘                                           │
│  ┌──────────────┐                                           │
│  │  返回首页    │  → 点击跳转 /                              │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 六、数据流

### 6.1 登录流程
```
用户点击"登录" → router.push('/login') → 登录页面
                  ↓
              输入凭证 → API 调用 → authStore.setToken()
                  ↓
          router.push('/admin/sources')
```

### 6.2 登出流程
```
用户点击"登出" → authStore.logout() → localStorage.removeItem('token')
                    ↓
              isLoggedIn = false
                    ↓
            保持在首页，按钮状态更新
```

---

## 七、文件清单

| 文件 | 操作 | 行数估计 |
|------|------|---------|
| `components/HeaderNav.vue` | 新建 | ~80 行 |
| `views/Home.vue` | 修改 | +20 行 |
| `views/Login.vue` | 修改 | +25 行 |
| `views/admin/Layout.vue` | 修改 | +35 行 |

---

## 八、测试要点

1. 首页未登录状态：只显示"登录"按钮
2. 首页已登录状态：显示"进入管理后台"和"登出"按钮
3. 登出功能：点击后清除 token 并更新按钮状态
4. 登录页返回按钮：点击后跳转到首页
5. 管理后台首页按钮：点击后跳转到首页
6. 移动端适配：所有按钮在小屏幕上正确显示
7. 响应式切换：窗口缩放时按钮样式正确变化

---

## 九、技术依赖

- Vue Router：`router.push()`, `<router-link>`
- Pinia Store：`useAuthStore()`
- Element Plus：样式参考（但不强制使用）
