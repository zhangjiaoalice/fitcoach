/**
 * API 请求客户端。
 *
 * 职责：
 *   1. 统一处理 baseURL（vite.config.ts 代理到后端）
 *   2. 自动带 Authorization: Bearer <token>
 *   3. 401 自动清 token + 跳登录
 *   4. 4xx/5xx 抛业务异常，供页面 catch
 */

const TOKEN_KEY = "fitcoach_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * 统一封装 fetch。
 * @param path 以 / 开头的路径，如 /auth/login；会自动拼上 /api 前缀
 * @param init 标准 fetch 选项
 */
export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = `/api${path}`;
  const headers = new Headers(init.headers ?? {});

  // 自动带 token
  const token = getToken();
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  // 有 body 时默认 JSON
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, { ...init, headers });

  // 401 视为登录失效
  if (response.status === 401) {
    clearToken();
    // 让路由守卫感知（M6 里会在 router.beforeEach 处理）
    window.location.hash = "#/login";
    throw new ApiError(401, "登录已过期，请重新登录");
  }

  if (!response.ok) {
    // 尝试解析 FastAPI 的 {"detail": "..."} 格式
    let detail = response.statusText;
    try {
      const body = await response.json();
      if (body && typeof body.detail === "string") detail = body.detail;
    } catch {
      /* 忽略解析错误 */
    }
    throw new ApiError(response.status, detail);
  }

  // 204 无内容
  if (response.status === 204) return undefined as T;

  return (await response.json()) as T;
}

// ─────────────────────────────────────────────
// 业务异常
// ─────────────────────────────────────────────
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
