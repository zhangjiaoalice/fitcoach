from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date

from app.models.water_log import WaterLog
from app.schemas.water_log import CreateWaterLog, UpdateWaterLog

async def create_water_log(db: AsyncSession, user_id: int, data: CreateWaterLog) -> WaterLog:
    """新建一条饮水记录"""
    water_log = WaterLog(user_id=user_id, **data.model_dump())
    db.add(water_log)
    await db.commit()
    await db.refresh(water_log)
    return water_log

async def sum_water_today(db, user_id: int, log_date: date) ->  int:
    """计算今天的饮水量,没数据的时候返回0"""
    stmt = select(func.coalesce(func.sum(WaterLog.ml), 0)).where(
        WaterLog.user_id == user_id,
        WaterLog.log_date == log_date
    )
    result = await db.execute(stmt)
    return int(result.scalar_one())