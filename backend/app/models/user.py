"""
User 表模型
- 一个继承Base的类 = 数据库中的一张表
- 类里每个 Mapped[...] 字段 = 表的一列
- SQLA alchemy2.0 推荐使用 Mapped[类型]+mapped_column(..) 的写法 
类型注解和列定义合二为一
"""
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class User(Base):
    # 指定这个模型对应数据库中的哪张表
    __tablename__ = "users"

    # 主键id, primary_key 会自动成为主键
    id: Mapped[int] = mapped_column(primary_key=True)

    # emial: 字符串、唯一（unique），建索引（index）, 不可为空
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # hashed_password: 字符串、不可为空，处理过的哈希值
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # created_at: 时间戳， 默认值 = 数据库当前时间（不用手动传）
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
