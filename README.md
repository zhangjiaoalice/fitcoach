# FitCoach Agent — AI 健身减脂教练（全栈项目）

> 全栈 AI Agent 项目

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TDesign Vue Next |
| 后端 | FastAPI + SQLAlchemy 2.0 (async) + Alembic |
| 数据库 | PostgreSQL 16 + pgvector |
| LLM | Moonshot / Kimi (OpenAI 兼容) |
| 部署 | Docker/Podman Compose + Nginx + 腾讯云 CVM |

## 目录结构

```
fitcoach/
├── docker-compose.yml        # 本地起PostgreSQL+pgvector（基建）
├── backend/
│   ├── requirements.txt
│   ├── .env.example          # 复制为 .env 填真实值
│   ├── app/
│   │   ├── main.py           # FastAPI 入口 ← 练习#2
│   │   ├── core/config.py    # 配置（基建）
│   │   ├── db/session.py     # 数据库连接 ← 练习#1
│   │   ├── models/           # ORM 表模型（M2起）
│   │   ├── schemas/          # Pydantic 请求/响应模型
│   │   ├── api/routes/       # 路由
│   │   ├── services/         # 业务逻辑
│   │   └── agent/            # Agent 引擎 + tools
│   └── tests/
└── frontend/# Vue3
```

## M0 快速启动

```bash
# 1. 起数据库（在 fitcoach/ 目录）
podman compose up -d          # 或 docker compose up -d

# 2. 后端环境
cd backend
cp .env.example .env

# 3. 启动
./.venv/bin/uvicorn app.main:app --reload

# 4. 验证
curl http://localhost:8000/health   # 期望 {"status":"ok","db":"connected"}
```

## 里程碑进度

- [ ] **M0** 脚手架 + Docker + PG连通 ← 当前
- [ ] M1 用户认证（JWT）
- [ ] M2 用户画像 CRUD
- [ ] M3 三大记录 CRUD
- [ ] M4 Moonshot 流式对话 + SSE
- [ ] M5 Tool Registry + 3 工具
- [ ] M6 Agent Loop 编排
- [ ] M7 周计划生成
- [ ] M8 RAG 知识库
- [ ] M9 Guardrails
- [ ] M10 Agent Trace
- [ ] M11 前端 Vue3
- [ ] M12 上线部署

model -> 迁移 -> schema -> service -> route