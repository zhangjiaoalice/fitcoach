<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { login, register } from "../api/auth";
import { ApiError } from "../api/client";
import { resetProfileCache } from "../router";
import Mascot from "../components/Mascot.vue";

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
    // 登录成功：清掉上次用户的画像缓存，让守卫重新查
    // 新注册的用户 getProfile 会返回 null → 守卫自动跳 /onboarding
    resetProfileCache();
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
      <Mascot type="momo" variant="full" :size="200" />
      <h1>FitCoach</h1>
      <p>和 Fit Momo 一起练出理想身材 💪</p>
    </div>
    <div class="tabs">
      <button :class="{ on: mode === 'login' }" @click="mode = 'login'">
        登录
      </button>
      <button :class="{ on: mode === 'register' }" @click="mode = 'register'">
        注册
      </button>
    </div>

    <form class="form" @submit.prevent="handleSubmit">
      <label>
        邮箱
        <input
          v-model="email"
          type="email"
          placeholder="you@fitcoach.com"
          autocomplete="email"
        />
      </label>
      <label>
        密码
        <input
          v-model="password"
          type="password"
          placeholder="至少 6 位"
          autocomplete="current-password"
        />
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
  height: 100vh;
  background: linear-gradient(180deg, #fffbf5 0%, #dbeafe 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 32px;
  overflow: hidden;
}
.brand {
  text-align: center;
  margin-bottom: 40px;
}
.logo {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: var(--brand-grad);
  color: var(--on-brand);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 500;
  margin: 0 auto 16px;
}
.brand h1 {
  font-size: 24px;
  font-weight: 500;
}
.brand p {
  font-size: 12px;
  color: var(--text-3);
  margin-top: 4px;
}

.tabs {
  display: flex;
  gap: 4px;
  width: 100%;
  max-width: 320px;
  background: var(--bg-elevated);
  border: 2px solid var(--glass-border);
  padding: 4px;
  border-radius: 10px;
  margin-bottom: 20px;
}
.tabs button {
  flex: 1;
  padding: 8px;
  border: 0;
  background: transparent;
  color: var(--text-3);
  font-size: 13px;
  border-radius: 8px;
  cursor: pointer;
}
.tabs button.on {
  background: var(--brand-grad);
  color: var(--on-brand);
}

.form {
  width: 100%;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.form label {
  font-size: 12px;
  color: var(--text-3);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form input {
  padding: 14px;
  border-radius: var(--radius-md);
  border: 2px solid var(--glass-border);
  background: var(--bg-elevated);
  color: var(--text-1);
  font-size: 15px;
  font-weight: 500;
}
.form input:focus {
  outline: 0;
  border-color: var(--brand);
}
.err {
  color: var(--warn);
  font-size: 12px;
  margin: 0;
}
.submit {
  margin-top: 8px;
  padding: 14px;
  border: 0;
  border-radius: var(--radius-md);
  background: var(--brand-grad);
  color: var(--on-brand);
  font-size: 15px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: var(--shadow-primary);
  transition: transform 0.1s, box-shadow 0.1s;
}
.submit:active {
  transform: translateY(2px);
  box-shadow: 0 0 0 var(--brand-dark);
}
.submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
