import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'dashboard', component: () => import('./views/DashboardView.vue') },
  { path: '/chat', name: 'chat', component: () => import('./views/ChatView.vue') },
  { path: '/diet', name: 'diet', component: () => import('./views/DietView.vue') },
  { path: '/me', name: 'me', component: () => import('./views/MeView.vue') },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
