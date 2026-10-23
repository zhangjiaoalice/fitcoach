import { apiFetch } from './client';

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
    latest_weight: number;
    measured_at: string;
}

export interface SleepSummary {
    duration_min: number;
    slept_at: string;
}

export interface RecordSummary {
    diet: DietSummary | null;
    workout: WorkoutSummary | null;
    water: WaterSummary | null;
    weight: WeightSummary | null;
    sleep: SleepSummary | null;
}

export async function getRecordSummary(): Promise<RecordSummary> {
    return await apiFetch('/record/summary');
}