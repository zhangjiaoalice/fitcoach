/**
 * 认证相关 API：登录 / 注册 / 拿当前用户
 */
import { apiFetch, setToken } from "./client";
import type { AuthCredentials, Token, UserOut } from "./types";

export async function login(credentials: AuthCredentials): Promise<Token> {
  const token = await apiFetch<Token>("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
  setToken(token.access_token);
  return token;
}

export async function register(credentials: AuthCredentials): Promise<UserOut> {
  return apiFetch<UserOut>("/auth/register", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export async function me(): Promise<UserOut> {
  return apiFetch<UserOut>("/auth/me");
}
