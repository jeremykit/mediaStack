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
        { path: 'system', name: 'admin-system', component: () => import('../views/admin/System.vue') }
      ]
    }
  ]
})

export default router
