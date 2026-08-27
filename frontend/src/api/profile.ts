/**
 * 用户画像 API
 */
import { apiFetch } from "./client";
import type { ProfileOut, ProfileUpsert } from "./types";

export async function getProfile(): Promise<ProfileOut | null> {
  try {
    return await apiFetch<ProfileOut>("/profile");
  } catch (err) {
    // 未创建画像时后端返回 404，前端当作 null
    if (err instanceof Error && "status" in err && (err as { status: number }).status === 404) {
      return null;
    }
    throw err;
  }
}

export async function upsertProfile(data: ProfileUpsert): Promise<ProfileOut> {
  return apiFetch<ProfileOut>("/profile", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}
