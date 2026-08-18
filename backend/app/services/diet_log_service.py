
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from datetime import date
from typing import List

from app.models.diet_logs import DietLog
from app.schemas.diet_log import DietLogCreate, DietLogUpdate


async def create_diet_log(db: AsyncSession, user_id: int, data: DietLogCreate) -> DietLog:
    """新建一条记录"""
    # **data.model_dump() 将orm 模型转换成 python 字典
    diet_log = DietLog(user_id=user_id, **data.model_dump())
    # 登记会话，将diet_log 对象挂载到会话待处理清淡
    db.add(diet_log)
    # commit 将会话里所有待处理的改动一次性提交到数据库,执行INSERT,数据真正新增
    await db.commit()
    # 从数据库重新查询一遍这条记录，把数据库中生成的最新值（id,created_at）填回到diet_log 对象上
    await db.refresh(diet_log)
    # 给前端返回完整对象（含数据库中生成的id,created_at）
    return diet_log

async def list_diet_log(db: AsyncSession, user_id: int, log_date: date)-> List[DietLog] | None:
    """根据日期查询日志列表"""
    stmt = select(DietLog).where(DietLog.user_id == user_id, DietLog.log_date == log_date)
    result = await db.execute(stmt)
    return result.scalars().all() or None

async def get_diet_log(db: AsyncSession, user_id: int, diet_id: int) -> DietLog:
    """根据id查询一条记录"""
    stmt = select(DietLog).where(DietLog.user_id == user_id, DietLog.id == diet_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_diet_log(db: AsyncSession, user_id: int, diet_id: int, data: DietLogUpdate) -> DietLog:
    """更新记录"""
    diet_log = await get_diet_log(db, user_id, diet_id)
    if diet_log is None:
        raise ValueError("没有找到这条记录")
    else:
        # exclude_unset = True 只更新前端真正传了的字段
        for k, v in data.model_dump(exclude_unset=True).items():
            # 已存在对像需要逐字段更新
            setattr(diet_log, k, v)
    await db.commit()
    await db.refresh(diet_log)
    return diet_log

async def delete_diet_log(db: AsyncSession, user_id: int, diet_id: int):
    """删除一条记录"""
    diet_log = await get_diet_log(db, user_id, diet_id)
    if diet_log is None:
        raise ValueError("没有找到这条记录")
    await db.delete(diet_log)
    await db.commit()

