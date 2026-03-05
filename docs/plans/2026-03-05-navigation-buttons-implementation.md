# 导航按钮功能实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在首页、登录页和管理后台之间添加导航按钮，实现便捷的页面跳转和用户状态管理

**Architecture:** 创建独立的 HeaderNav 组件封装首页导航逻辑，在 Home.vue/Login.vue/Layout.vue 中按需引入，使用 Pinia auth store 管理登录状态

**Tech Stack:** Vue 3 (Composition API), Vue Router, Pinia, Element Plus

---

## Task 1: 创建 HeaderNav 组件

**Files:**
- Create: `frontend/src/components/HeaderNav.vue`

**Step 1: 创建 HeaderNav.vue 组件文件**

```vue
<template>
  <div class="header-nav">
    <router-link
      v-if="!authStore.isLoggedIn"
      to="/login"
      class="nav-btn login-btn"
    >
      登录
    </router-link>
    <template v-else>
      <router-link
        to="/admin/sources"
        class="nav-btn admin-btn"
      >
        进入管理后台
      </router-link>
      <button
        @click="handleLogout"
        class="nav-btn logout-btn"
      >
        登出
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
  ElMessage.success('已登出')
}
</script>

<style scoped>
.header-nav {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
  z-index: 10;
}

.nav-btn {
  padding: 10px 20px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  font-family: var(--font-sans);
}

.login-btn {
  background: linear-gradient(135deg, #FF6B9D 0%, #FFA06B 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(255, 107, 157, 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4);
}

.admin-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #FF6B9D;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.admin-btn:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.logout-btn {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.5);
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.8);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .header-nav {
    top: 16px;
    right: 16px;
    gap: 8px;
  }

  .nav-btn {
    padding: 8px 16px;
    font-size: 13px;
    border-radius: 20px;
  }

  .admin-btn {
    display: none;
  }
}
</style>
```

**Step 2: 提交**

```bash
cd frontend
git add src/components/HeaderNav.vue
git commit -m "feat: create HeaderNav component for homepage navigation"
```

---

## Task 2: 在首页引入 HeaderNav 组件

**Files:**
- Modify: `frontend/src/views/Home.vue`

**Step 1: 在 script setup 中导入 HeaderNav 组件**

在 `import VideoCard from '../components/VideoCard.vue'` 后添加：

```vue
import HeaderNav from '../components/HeaderNav.vue'
```

**Step 2: 在模板中添加 HeaderNav 组件**

在 `<div class="hero-content">` 内，`<div class="brand-area">` 之前添加：

```vue
<HeaderNav />
```

**Step 3: 调整 brand-area 的上边距以适配导航栏**

修改 `.brand-area` 的样式，添加 `margin-top: 20px;`：

```css
.brand-area {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
  margin-bottom: 40px;
  justify-content: center;
}
```

**Step 4: 提交**

```bash
cd frontend
git add src/views/Home.vue
git commit -m "feat: add HeaderNav to homepage"
```

---

## Task 3: 在登录页添加返回首页按钮

**Files:**
- Modify: `frontend/src/views/Login.vue`

**Step 1: 在登录按钮下方添加返回首页链接**

在 `</el-form>` 后，`<!-- Status Indicator -->` 前添加：

```vue
<!-- Back to Home -->
<router-link to="/" class="back-to-home-btn">
  返回首页
</router-link>
```

**Step 2: 添加返回首页按钮的样式**

在 `.login-button:active` 样式后添加：

```css
/* Back to Home Button */
.back-to-home-btn {
  display: block;
  width: 100%;
  height: 48px;
  line-height: 44px;
  text-align: center;
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  margin-top: 16px;
  text-decoration: none;
  transition: all 0.3s ease;
  font-family: var(--font-sans);
}

.back-to-home-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}

.back-to-home-btn:active {
  transform: translateY(0);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .back-to-home-btn {
    height: 44px;
    line-height: 40px;
    font-size: 14px;
    margin-top: 12px;
  }
}
```

**Step 3: 提交**

```bash
cd frontend
git add src/views/Login.vue
git commit -m "feat: add back to home button on login page"
```

---

## Task 4: 在管理后台添加首页跳转按钮

**Files:**
- Modify: `frontend/src/views/admin/Layout.vue`

**Step 1: 在 header-right 中添加首页按钮**

修改 `<div class="header-right">` 内容：

```vue
<div class="header-right">
  <router-link to="/" class="home-link-btn" title="返回首页">
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M9 22V12H15V22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <span class="home-text">首页</span>
  </router-link>
  <SystemStatus />
</div>
```

**Step 2: 添加首页按钮样式**

在 `.header-right` 样式后添加：

```css
.home-link-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.home-link-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(233, 69, 96, 0.3);
  color: white;
}

.home-link-btn svg {
  width: 18px;
  height: 18px;
}

.home-text {
  font-size: 14px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .home-text {
    display: none;
  }

  .home-link-btn {
    padding: 8px;
  }

  .home-link-btn svg {
    width: 20px;
    height: 20px;
  }
}
```

**Step 3: 提交**

```bash
cd frontend
git add src/views/admin/Layout.vue
git commit -m "feat: add home link button in admin layout header"
```

---

## Task 5: 测试功能

**Step 1: 启动开发服务器**

```bash
cd frontend
npm run dev
```

**Step 2: 手动测试清单**

- [ ] 访问首页 `/`，未登录状态应显示"登录"按钮
- [ ] 点击"登录"按钮，跳转到登录页
- [ ] 在登录页点击"返回首页"，跳转回首页
- [ ] 登录成功后，首页右上角显示"进入管理后台"和"登出"按钮
- [ ] 点击"进入管理后台"，跳转到 `/admin/sources`
- [ ] 在管理后台点击右上角"首页"按钮，跳转回首页
- [ ] 点击"登出"按钮，显示"已登出"提示，按钮变为"登录"
- [ ] 移动端：调整浏览器宽度至 < 768px，验证按钮样式正确显示

**Step 3: 如有测试问题，记录并修复**

**Step 4: 测试通过后提交**

```bash
cd frontend
git commit --allow-empty -m "test: verify navigation buttons functionality"
```

---

## Task 6: 更新需求文档（如需要）

**Files:**
- Check: `docs/requirements.md`

**Step 1: 检查需求文档是否需要更新**

如果需求文档中缺少导航按钮相关描述，添加相应内容。

**Step 2: 如有更新，提交**

```bash
git add docs/requirements.md
git commit -m "docs: update requirements for navigation buttons feature"
```

---

## 测试验收标准

1. 首页导航组件根据登录状态正确显示对应按钮
2. 所有导航按钮点击后正确跳转到目标页面
3. 登出功能正确清除 token 并更新 UI 状态
4. 移动端样式适配正确（按钮尺寸、布局）
5. 过渡动画流畅自然

---

## 相关文档参考

- 设计文档: `docs/plans/2026-03-05-navigation-buttons-design.md`
- 项目说明: `CLAUDE.md`
- Router 配置: `frontend/src/router/index.ts`
- Auth Store: `frontend/src/stores/auth.ts`
