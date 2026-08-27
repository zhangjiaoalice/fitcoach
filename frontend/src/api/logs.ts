/**
 * 三大记录 API：饮食 / 训练 / 体重
 */
import { apiFetch } from "./client";
import type {
  DietLogCreate,
  DietLogOut,
  WeightLogCreate,
  WeightLogOut,
  WorkoutLogCreate,
  WorkoutLogOut,
} from "./types";

// ─────────────────────────── 饮食 ───────────────────────────
export function listDietLogs(logDate: string): Promise<DietLogOut[]> {
  return apiFetch<DietLogOut[]>(`/diet-logs?log_date=${logDate}`);
}
export function createDietLog(data: DietLogCreate): Promise<DietLogOut> {
  return apiFetch<DietLogOut>("/diet-logs", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
export function deleteDietLog(id: number): Promise<void> {
  return apiFetch<void>(`/diet-logs/${id}`, { method: "DELETE" });
}

// ─────────────────────────── 训练 ───────────────────────────
export function listWorkoutLogs(logDate: string): Promise<WorkoutLogOut[]> {
  return apiFetch<WorkoutLogOut[]>(`/workout-logs?log_date=${logDate}`);
}
export function createWorkoutLog(data: WorkoutLogCreate): Promise<WorkoutLogOut> {
  return apiFetch<WorkoutLogOut>("/workout-logs", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
export function deleteWorkoutLog(id: number): Promise<void> {
  return apiFetch<void>(`/workout-logs/${id}`, { method: "DELETE" });
}

// ─────────────────────────── 体重 ───────────────────────────
export function listWeightLogs(logDate: string): Promise<WeightLogOut[]> {
  return apiFetch<WeightLogOut[]>(`/weight-logs?log_date=${logDate}`);
}
export function createWeightLog(data: WeightLogCreate): Promise<WeightLogOut> {
  return apiFetch<WeightLogOut>("/weight-logs", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
export function deleteWeightLog(id: number): Promise<void> {
  return apiFetch<void>(`/weight-logs/${id}`, { method: "DELETE" });
}
