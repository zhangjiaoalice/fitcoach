# FitCoach 后端 Docker 镜像
# 多阶段构建: builder 装依赖 -> runtime 只带必要文件,镜像更瘦

FROM python:3.13-slim AS builder

WORKDIR /app

# 系统依赖: asyncpg 需要 gcc / libpq
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 先拷贝依赖清单,让 layer 缓存生效(改代码不用重装依赖)
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================================
FROM python:3.13-slim AS runtime

WORKDIR /app

# runtime 也需要 libpq (asyncpg 运行时)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 拿装好的 pip 包
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 业务代码
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

EXPOSE 8000

# 生产用 uvicorn --workers,不加 --reload (会额外占内存)
# --host 0.0.0.0 是容器内必需
# 启动前先跑迁移(alembic upgrade head),确保数据库表结构最新
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
