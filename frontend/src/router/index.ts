import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/verify',
      name: 'verify',
      component: () => import('../views/Verify.vue')
    },
    {
      path: '/video/:id',
      name: 'video-detail',
      component: () => import('../views/VideoDetail.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/Layout.vue'),
      children: [
        { path: 'sources', name: 'admin-sources', component: () => import('../views/admin/Sources.vue') },
        { path: 'tasks', name: 'admin-tasks', component: () => import('../views/admin/Tasks.vue') },
        { path: 'schedules', name: 'admin-schedules', component: () => import('../views/admin/Schedules.vue') },
        { path: 'videos', name: 'admin-videos', component: () => import('../views/admin/Videos.vue') },
        { path: 'system', name: 'admin-system', component: () => import('../views/admin/System.vue') },
        { path: 'categories', name: 'admin-categories', component: () => import('../views/admin/Categories.vue') },
        { path: 'tags', name: 'admin-tags', component: () => import('../views/admin/Tags.vue') },
        { path: 'view-codes', name: 'admin-view-codes', component: () => import('../views/admin/ViewCodes.vue') },
        { path: 'upload', name: 'admin-upload', component: () => import('../views/admin/Upload.vue') }
      ]
    }
  ]
})

export default router
