import { createRouter, createWebHashHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

import { getToken } from "./api/client";

const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/dashboard" },
  {
    path: "/login",
    name: "login",
    component: () => import("./views/LoginView.vue"),
    meta: { public: true },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import("./views/DashboardView.vue"),
  },
  {
    path: "/chat",
    name: "chat",
    component: () => import("./views/ChatView.vue"),
  },
  {
    path: "/diet",
    name: "diet",
    component: () => import("./views/DietView.vue"),
  },
  {
    path: "/me",
    name: "me",
    component: () => import("./views/MeView.vue"),
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// 登录守卫：未登录访问受保护页 → 跳 /login
router.beforeEach((to) => {
  if (to.meta.public) return true;
  if (!getToken()) return { name: "login" };
  return true;
});

export default router;
