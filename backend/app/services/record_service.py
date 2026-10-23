from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import date

from app.schemas.record import RecordSummary, DietSummary,  WorkoutSummary, WeightSummary
from app.services.diet_log_service import list_diet_log
from app.services.weight_log_service import list_weight_recent
from app.services.workout_log_service import list_workout_log

async def get_record_summary(db: AsyncSession, user_id: int) -> RecordSummary:
    today = date.today()

    # 子任务： 饮食记录
    diet_logs = await list_diet_log(db, user_id, today)
    diet = None
    if diet_logs:
        # 累加 kcal、计数 meals
        total_kcal = sum(d.calories_kcal or 0 for d in diet_logs)
        diet = DietSummary(kcal=total_kcal, meal_count=len(diet_logs))


    # 子任务： 训练记录
    workouts = await list_workout_log(db, user_id, today)
    workout = None
    if workouts:
        # 当天记录的任务都算完成
        done = len(workouts)
        total = len(workouts)
        workout = WorkoutSummary(done=done, total = total, est_kcal=0)
        # est_kcal 预估消耗，mvp 先给 0 或根据 duration 估算

    # 子任务： 体重变化记录
    recent = await list_weight_recent(db, user_id, 7)
    weight = None
    if recent:
        # 日期对象之间是可以比较大小的，日期越晚，越接近今天
        latest_log = max(recent, key=lambda x: x.log_date)
        weight = WeightSummary(latest_kg=latest_log.weight_kg, measured_at=latest_log.log_date)

    # 子任务： 饮水记录
    water = None

    # 子任务： 睡眠
    sleep = None

    return RecordSummary(diet=diet, workout=workout, weight=weight, water=water, sleep=sleep)

