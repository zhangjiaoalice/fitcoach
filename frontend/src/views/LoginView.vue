<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { login, register } from "../api/auth";
import { ApiError } from "../api/client";

const router = useRouter();

const mode = ref<"login" | "register">("login");
const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMsg = ref("");

async function handleSubmit(): Promise<void> {
  if (!email.value || !password.value) {
    errorMsg.value = "请输入邮箱和密码";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  try {
    if (mode.value === "register") {
      await register({ email: email.value, password: password.value });
      // 注册完立即登录
    }
    await login({ email: email.value, password: password.value });
    router.push({ name: "dashboard" });
  } catch (err) {
    errorMsg.value = err instanceof ApiError ? err.message : "请求失败，请重试";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-wrap">
    <div class="brand">
      <div class="logo">FC</div>
      <h1>FitCoach</h1>
      <p>AI 健身减脂教练</p>
    </div>

    <div class="tabs">
      <button :class="{ on: mode === 'login' }" @click="mode = 'login'">登录</button>
      <button :class="{ on: mode === 'register' }" @click="mode = 'register'">注册</button>
    </div>

    <form class="form" @submit.prevent="handleSubmit">
      <label>
        邮箱
        <input v-model="email" type="email" placeholder="you@fitcoach.com" autocomplete="email" />
      </label>
      <label>
        密码
        <input v-model="password" type="password" placeholder="至少 6 位" autocomplete="current-password" />
      </label>
      <p v-if="errorMsg" class="err">{{ errorMsg }}</p>
      <button class="submit" type="submit" :disabled="loading">
        {{ loading ? "请稍候…" : mode === "login" ? "登录" : "注册并登录" }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.login-wrap {
  min-height: 100vh;
  background: var(--bg-app);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 32px;
}
.brand { text-align: center; margin-bottom: 40px; }
.logo {
  width: 64px; height: 64px; border-radius: 20px;
  background: var(--brand-grad); color: var(--on-brand);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 500;
  margin: 0 auto 16px;
}
.brand h1 { font-size: 24px; font-weight: 500; }
.brand p { font-size: 12px; color: var(--text-3); margin-top: 4px; }

.tabs {
  display: flex; gap: 4px; width: 100%; max-width: 320px;
  background: rgba(255, 255, 255, 0.04); padding: 4px; border-radius: 10px;
  margin-bottom: 20px;
}
.tabs button {
  flex: 1; padding: 8px; border: 0; background: transparent;
  color: var(--text-3); font-size: 13px; border-radius: 8px; cursor: pointer;
}
.tabs button.on { background: var(--brand-grad); color: var(--on-brand); }

.form { width: 100%; max-width: 320px; display: flex; flex-direction: column; gap: 14px; }
.form label { font-size: 12px; color: var(--text-3); display: flex; flex-direction: column; gap: 6px; }
.form input {
  padding: 12px; border-radius: 10px; border: 1px solid var(--hairline);
  background: rgba(255, 255, 255, 0.04); color: var(--text-1); font-size: 14px;
}
.form input:focus { outline: 0; border-color: var(--brand); }
.err { color: var(--warn); font-size: 12px; margin: 0; }
.submit {
  margin-top: 8px; padding: 12px; border: 0; border-radius: 12px;
  background: var(--brand-grad); color: var(--on-brand); font-size: 14px; font-weight: 500;
  cursor: pointer;
}
.submit:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
