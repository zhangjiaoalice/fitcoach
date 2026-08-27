/**
 * 后端 API 的请求 / 响应类型定义。
 * 对应 backend/app/schemas/*.py 里的 Pydantic 模型。
 *
 * 命名约定：
 *   - XxxCreate / XxxUpdate：请求体
 *   - XxxOut：后端返回体
 *   - 小写下划线字段名（与后端一致，不做 camelCase 转换）
 */

// ─────────────────────────────────────────────
// 认证
// ─────────────────────────────────────────────
export interface AuthCredentials {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserOut {
  id: number;
  email: string;
  created_at: string;
}

// ─────────────────────────────────────────────
// 用户画像 (对应 M2)
// ─────────────────────────────────────────────
export interface ProfileUpsert {
  gender?: string | null;
  age: number;
  height_cm: number;
  current_weight_kg: number;
  target_weight_kg: number;
  activity_level: string;
  training_days_per_week: number;
  diet_preference?: string | null;
  health_notes?: string | null;
  goal_description?: string | null;
}

export interface ProfileOut extends ProfileUpsert {
  id: number;
  user_id: number;
  created_at: string;
}

// ─────────────────────────────────────────────
// 饮食记录 (对应 M3)
// ─────────────────────────────────────────────
export type MealType = "breakfast" | "lunch" | "dinner" | "snack" | string;
export type LogSource = "manual" | "agent";

export interface DietLogCreate {
  log_date: string; // YYYY-MM-DD
  meal_type: MealType;
  food_name: string;
  source: LogSource;
  amount_text?: string | null;
  calories_kcal?: number | null;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
  raw_text?: string | null;
}

export interface DietLogOut extends DietLogCreate {
  id: number;
  user_id: number;
  created_at: string;
}

// ─────────────────────────────────────────────
// 训练记录
// ─────────────────────────────────────────────
export interface WorkoutLogCreate {
  log_date: string;
  workout_type: string;
  duration_min: number;
  intensity?: string | null;
  note?: string | null;
}

export interface WorkoutLogOut extends WorkoutLogCreate {
  id: number;
  user_id: number;
  created_at: string;
}

// ─────────────────────────────────────────────
// 体重记录
// ─────────────────────────────────────────────
export interface WeightLogCreate {
  log_date: string;
  weight_kg: number;
  waist_cm?: number | null;
  note?: string | null;
}

export interface WeightLogOut extends WeightLogCreate {
  id: number;
  user_id: number;
  created_at: string;
}

// ─────────────────────────────────────────────
// Agent 对话 (对应 M4)
// ─────────────────────────────────────────────
export interface AgentToolCall {
  name: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface ChatIn {
  message: string;
}

export interface ChatOut {
  reply: string;
  iterations: number;
  tool_calls: AgentToolCall[];
}
