import { createRouter, createWebHashHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

import { getToken } from "./api/client";
import { getProfile } from "./api/profile";

// 画像完成状态缓存：避免每次路由跳转都请求 /profile
// null = 未查过；true = 已完成；false = 未完成
let profileCompletedCache: boolean | null = null;

/** 外部可调用：登录/注册完 or 完成 onboarding 后更新缓存 */
export function setProfileCompleted(done: boolean): void {
  profileCompletedCache = done;
}

/** 外部可调用：登出时重置 */
export function resetProfileCache(): void {
  profileCompletedCache = null;
}

const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/dashboard" },
  {
    path: "/login",
    name: "login",
    component: () => import("./views/LoginView.vue"),
    meta: { public: true, hideTabbar: true },
  },
  {
    path: "/onboarding",
    name: "onboarding",
    component: () => import("./views/OnboardingView.vue"),
    meta: { requiresAuth: true, hideTabbar: true, skipProfileCheck: true },
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

// 登录守卫 + Onboarding 守卫
// 1. 未登录访问受保护页 → 跳 /login
// 2. 登录了但未完成画像 → 强制 /onboarding（避免直接进 /dashboard 空荡荡）
router.beforeEach(async (to) => {
  if (to.meta.public) return true;

  // 登录检查
  if (to.meta.requiresAuth && !getToken()) {
    profileCompletedCache = null;
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  // onboarding 自己这个页面不走画像检查，避免循环重定向
  if (to.meta.skipProfileCheck) return true;

  // 画像完整性检查（首次导航查一次，之后用缓存）
  if (profileCompletedCache === null) {
    try {
      const profile = await getProfile();
      profileCompletedCache = profile !== null;
    } catch {
      // 查画像失败不阻断（可能后端挂了，让用户先进去用）
      profileCompletedCache = true;
    }
  }

  if (!profileCompletedCache) {
    return { name: "onboarding" };
  }

  return true;
});

export default router;
