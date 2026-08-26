"""Alembic 迁移环境配置（已改造为异步 + 读取项目配置与模型）。

这个文件是基建（AI 已配好），你理解即可，不用手敲。关键改动：
1. 从 app.core.config 读 DATABASE_URL（不再用 alembic.ini 里的假地址）
2. 导入 Base 和所有模型，让 autogenerate 能"看见"你的表
3. 用异步引擎跑迁移（配合项目的 asyncpg）
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import get_settings
from app.db.session import Base
# 关键：这里必须 import 每个模型，Base.metadata 才会包含它们。
# 以后新增模型（M2 的 profile、M3 的 diet_logs...）都要在这里加一行 import。
from app.models.user import User  # noqa: F401
from app.models.profile import Profile  # noqa: F401
from app.models.diet_log import DietLog  # noqa: F401
from app.models.workout_log import WorkoutLog  # noqa: F401
from app.models.weight_log import WeightLog  # noqa: F401
from app.models.agent_traces import AgentTrace  # noqa: F401

config = context.config

# 用项目 .env 里的真实数据库地址覆盖 alembic.ini 的占位值
config.set_main_option("sqlalchemy.url", get_settings().database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate 依据：Base 收集到的所有表结构
target_metadata = Base.metadata


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


#迁移只走online（异步）模式
run_migrations_online()
