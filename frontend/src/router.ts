import { createRouter, createWebHashHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

import { getToken } from "./api/client";

const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/dashboard" },
  {
    path: "/login",
    name: "login",
    component: () => import("./views/LoginView.vue"),
    meta: { public: true, hideTabbar: true },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import("./views/DashboardView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/chat",
    name: "chat",
    component: () => import("./views/ChatView.vue"),
    meta: { hideTabbar: true, requiresAuth: true }, // 教练是二级页面，不显示底部 tabbar
  },
  {
    path: "/diet",
    name: "diet",
    component: () => import("./views/DietView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/me",
    name: "me",
    component: () => import("./views/MeView.vue"),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// 登录守卫：未登录访问受保护页 → 跳 /login
router.beforeEach((to) => {
  if (to.meta.public) return true;
  if (to.meta.requiresAuth && !getToken()) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  return true;
});

export default router;
