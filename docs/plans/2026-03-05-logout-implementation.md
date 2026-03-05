# 登出按钮功能实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在用户首页和管理后台添加带确认对话框的登出按钮功能

**Architecture:** 利用现有的 authStore.logout() 方法，在 HeaderNav 和 admin/Layout 组件中添加带 ElMessageBox.confirm 的登出逻辑。

**Tech Stack:** Vue 3, Element Plus (ElMessageBox), Pinia (authStore), Vue Router

---

## Task 1: 用户首页 HeaderNav 添加确认对话框

**Files:**
- Modify: `frontend/src/components/HeaderNav.vue:27-38`

**Step 1: 修改 handleLogout 函数，添加确认对话框**

在 `<script setup>` 部分修改 handleLogout 函数：

```typescript
import { ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要登出吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    // 用户点击确定
    authStore.logout()
    ElMessage.success('已登出')
    // 刷新当前页面以更新UI状态
    router.go(0)
  } catch {
    // 用户点击取消，什么都不做
  }
}
```

**Step 2: 添加 ElMessageBox 导入**

确保 `<script setup>` 顶部已有：
```typescript
import { ElMessageBox, ElMessage } from 'element-plus'
```

**Step 3: 验证功能**

1. 启动前端：`cd frontend && npm run dev`
2. 访问 http://localhost:5173
3. 登录后点击"登出"按钮
4. 应弹出确认对话框
5. 点击"取消"应关闭对话框，留在当前页面
6. 点击"确定"应登出并刷新页面，按钮变为"登录"

**Step 4: 提交**

```bash
git add frontend/src/components/HeaderNav.vue
git commit -m "feat: add confirmation dialog for logout on home page"
```

---

## Task 2: 管理后台 Layout 顶部添加登出按钮

**Files:**
- Modify: `frontend/src/views/admin/Layout.vue:126-139` (top-header 区域)
- Modify: `frontend/src/views/admin/Layout.vue:161-172` (script setup 部分)

**Step 1: 在 script setup 部分添加登出逻辑**

在 `import { watch } from 'vue'` 之前添加：

```typescript
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要登出吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    authStore.logout()
    ElMessage.success('已登出')
    // 管理后台登出后跳转到登录页
    router.push('/login')
  } catch {
    // 用户取消
  }
}
```

**Step 2: 在顶部 header-right 区域添加登出按钮**

修改 top-header 中的 header-right 部分：

```vue
<div class="header-right">
  <router-link to="/" class="home-link-btn" title="返回首页">
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.7893 3 20.5304 3 20V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M9 22V12H15V22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <span class="home-text">首页</span>
  </router-link>
  <!-- 新增登出按钮 -->
  <button @click="handleLogout" class="logout-header-btn" title="登出">
    <svg class="logout-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="11" width="10" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
      <path d="M7 11V7C7 5.34315 8.34315 4 10 4H14C15.6569 4 17 5.34315 17 7V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      <path d="M17 15L19 17M17 15V19M17 15H13M19 17H15M19 17V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <span>登出</span>
  </button>
  <SystemStatus />
</div>
```

**Step 3: 添加登出按钮样式**

在 `<style scoped>` 部分，在 `.home-link-btn` 样式后添加：

```css
.logout-header-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(233, 69, 96, 0.1);
  border: 1px solid rgba(233, 69, 96, 0.3);
  border-radius: 8px;
  color: #E94560;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.logout-header-btn:hover {
  background: rgba(233, 69, 96, 0.2);
  border-color: rgba(233, 69, 96, 0.5);
  transform: translateY(-1px);
}

.logout-icon {
  width: 18px;
  height: 18px;
}
```

**Step 4: 验证功能**

1. 访问管理后台任意页面
2. 顶部 header 应显示"🔒 登出"按钮
3. 点击应弹出确认对话框
4. 确认后应跳转到登录页

**Step 5: 提交**

```bash
git add frontend/src/views/admin/Layout.vue
git commit -m "feat: add logout button to admin header with confirmation"
```

---

## Task 3: 管理后台侧边栏底部添加登出按钮

**Files:**
- Modify: `frontend/src/views/admin/Layout.vue:106-120` (sidebar-footer 区域)

**Step 1: 修改 sidebar-footer 结构**

将 user-profile 改为包含登出按钮的结构：

```vue
<!-- Sidebar Footer -->
<div class="sidebar-footer">
  <div class="user-profile" @click="handleLogout">
    <div class="user-avatar">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2" />
        <path d="M6 21C6 17.134 8.686 14 12 14C15.314 14 18 17.134 18 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      </svg>
    </div>
    <div class="user-info">
      <div class="user-name">Admin</div>
      <div class="user-role">管理员</div>
    </div>
    <div class="logout-sidebar-icon">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="11" width="10" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
        <path d="M7 11V7C7 5.34315 8.34315 4 10 4H14C15.6569 4 17 5.34315 17 7V11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M17 15L19 17M17 15V19M17 15H13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
  </div>
</div>
```

**Step 2: 添加侧边栏登出图标样式**

在 `.user-role` 样式后添加：

```css
.logout-sidebar-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: rgba(233, 69, 96, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #E94560;
  transition: all 0.3s ease;
}

.user-profile:hover .logout-sidebar-icon {
  background: rgba(233, 69, 96, 0.2);
}

.logout-sidebar-icon svg {
  width: 16px;
  height: 16px;
}
```

**Step 3: 移动端样式调整**

确保移动端也正确显示登出图标。在 `@media (max-width: 768px)` 的 `.user-avatar` 样式后添加：

```css
.logout-sidebar-icon {
  width: 28px;
  height: 28px;
}

.logout-sidebar-icon svg {
  width: 14px;
  height: 14px;
}
```

**Step 4: 验证功能**

1. 访问管理后台
2. 侧边栏底部用户区域应显示登出图标
3. 鼠标悬停应有高亮效果
4. 点击应弹出确认对话框并执行登出

**Step 5: 提交**

```bash
git add frontend/src/views/admin/Layout.vue
git commit -m "feat: add logout icon to admin sidebar footer"
```

---

## Task 4: 整体测试验证

**Step 1: 测试用户首页登出**

1. 启动前端：`cd frontend && npm run dev`
2. 访问 http://localhost:5173
3. 点击"登录"按钮登录
4. 登录后应显示"进入管理后台"和"登出"按钮
5. 点击"登出"
6. 应弹出确认对话框："确定要登出吗？"
7. 点击"取消"，对话框关闭，留在首页
8. 再次点击"登出"，点击"确定"
9. 应显示"已登出"消息，页面刷新
10. 刷新后应显示"登录"按钮

**Step 2: 测试管理后台顶部登出**

1. 登录后点击"进入管理后台"
2. 顶部 header 应显示"首页"和"🔒 登出"按钮
3. 点击"登出"按钮
4. 应弹出确认对话框
5. 点击"确定"后应跳转到登录页

**Step 3: 测试管理后台侧边栏登出**

1. 登录管理后台
2. 侧边栏底部用户区域右侧应显示锁图标
3. 点击用户区域或锁图标
4. 应弹出确认对话框
5. 点击"确定"后应跳转到登录页

**Step 4: 跨浏览器测试**

在 Chrome、Firefox、Edge 中验证上述功能

**Step 5: 移动端测试**

使用浏览器开发者工具切换到移动视图，验证：
- 移动端登出按钮布局正确
- 触摸交互正常

**Step 6: 最终提交**

```bash
git add frontend/src/components/HeaderNav.vue frontend/src/views/admin/Layout.vue
git commit --amend -m "feat: add logout buttons with confirmation dialog to home page and admin panel"
```

---

## 验收清单

- [ ] 用户首页点击登出弹出确认对话框
- [ ] 用户首页取消登出留在当前页面
- [ ] 用户首页确认登出后刷新页面，状态更新
- [ ] 管理后台顶部显示登出按钮
- [ ] 管理后台顶部登出确认后跳转登录页
- [ ] 管理后台侧边栏显示登出图标
- [ ] 管理后台侧边栏登出确认后跳转登录页
- [ ] 所有对话框标题为"提示"，内容为"确定要登出吗？"
- [ ] 登出成功后显示"已登出"消息
