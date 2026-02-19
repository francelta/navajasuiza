import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/employees',
    name: 'AdminEmployees',
    component: () => import('@/views/AdminEmployeesView.vue'),
    meta: { requiresAuth: true, requiresSuperAdmin: true },
  },
  {
    path: '/tools/klaes',
    name: 'KlaesReprocess',
    component: () => import('@/views/KlaesReprocessView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/config/setup',
    name: 'EnvSetup',
    component: () => import('@/views/EnvSetupView.vue'),
    meta: { requiresAuth: true, requiresSuperAdmin: true },
  },
  {
    path: '/klaes/manager',
    name: 'KlaesManager',
    component: () => import('@/views/KlaesManagerView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/ReportsView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.requiresSuperAdmin && !auth.isSuperAdmin) {
    next({ name: 'Dashboard' })
  } else if (to.meta.requiresGuest && auth.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
