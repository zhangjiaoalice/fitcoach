import { apiFetch } from "./client";

/**
 * 记录 tab 聚合摘要，和 backend app/schemas/record.py 字段对齐。
 * 任意子项为 null 代表当天没数据，前端渲染空态。
 */

export interface DietSummary {
  kcal: number;
  meal_count: number;
}

export interface WorkoutSummary {
  done: number;
  total: number;
  est_kcal: number;
}

export interface WaterSummary {
  ml: number;
  target_ml: number;
}

export interface WeightSummary {
  latest_kg: number; // 后端字段名是 latest_kg，不是 latest_weight
  measured_at: string; // date → ISO "YYYY-MM-DD"
}

export interface SleepSummary {
  duration_min: number;
  slept_at: string | null; // datetime | None
}

export interface RecordSummary {
  diet: DietSummary | null;
  workout: WorkoutSummary | null;
  water: WaterSummary | null;
  weight: WeightSummary | null;
  sleep: SleepSummary | null;
}

export async function getRecordSummary(): Promise<RecordSummary> {
  return await apiFetch<RecordSummary>("/record/summary");
}
