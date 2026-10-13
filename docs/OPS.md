# FitCoach 运维小抄

> 本地改完代码 → 推送到云 CVM → 重建容器 → 验证。
> 服务器: `root@43.137.46.175`，项目路径 `/root/fitcoach/`，入口 `http://43.137.46.175:8080`。

---

## 🚀 常规发版（本地改完 → 上线）

### ① 本地推代码

```bash
cd /Users/alice/Desktop/fitcoach

rsync -avz --delete \
  --exclude '.venv' \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'dist' \
  --exclude '.env' \
  --exclude '.DS_Store' \
  ./ root@43.137.46.175:/root/fitcoach/
```

**关键**：
- `--exclude '.env'` 保护服务器 `.env.prod` 不被覆盖
- `--delete` 让服务器与本地保持一致
- 卡住加 `--timeout=30 --partial`

### ② SSH 重建容器

```bash
ssh root@43.137.46.175
cd /root/fitcoach
```

按改动范围选一种：

| 改动 | 命令 |
|---|---|
| 只改 Python/Vue 代码 | `docker compose -f docker-compose.prod.yml up -d --build backend web` |
| 改了 `requirements.txt` | `docker compose -f docker-compose.prod.yml build --no-cache backend && docker compose -f docker-compose.prod.yml up -d backend` |
| 改了前端 `package.json` | `docker compose -f docker-compose.prod.yml build --no-cache web && docker compose -f docker-compose.prod.yml up -d web` |
| 一键全重建 | `docker compose -f docker-compose.prod.yml up -d --build` |

### ③ 验证

```bash
# 服务器上
docker compose -f docker-compose.prod.yml ps                     # 看 3 个容器 Up (healthy)
docker compose -f docker-compose.prod.yml logs -f --tail=50 backend  # 看到 Uvicorn running on 0.0.0.0:8000 即可
curl http://localhost:8080/api/health                            # {"status":"ok","db":"connected"}
```

**本地浏览器**打开 `http://43.137.46.175:8080`，登录试一条消息。

---

## 🗄️ 有 model 改动？跑迁移

```bash
# 容器重建完成后（服务器上）
docker exec -it fitcoach-backend-prod python -m alembic upgrade head
```

> model 没动就跳过这步。

---

## 🔧 日常运维命令

```bash
# 看最后 100 行日志
docker compose -f docker-compose.prod.yml logs --tail=100 backend

# 进容器
docker exec -it fitcoach-backend-prod bash

# 重启某个服务（不重建镜像）
docker compose -f docker-compose.prod.yml restart backend

# 清理旧镜像释放磁盘
docker system prune -af

# 看容器资源占用
docker stats --no-stream
```

---

## 💾 备份 & 恢复

### 查看自动备份
```bash
# 服务器上
ls -lh /root/backup/            # 每天凌晨 3 点自动备份，保留 14 天
cat /var/log/cron | grep backup # 查备份是否正常执行
```

### 手动备份
```bash
# 服务器上
docker exec fitcoach-db-prod pg_dump -U fitcoach -d fitcoach \
  | gzip > /root/backup/manual-$(date +%Y%m%d-%H%M).sql.gz
```

### 从备份恢复
```bash
# 服务器上
gunzip -c /root/backup/xxx.sql.gz | \
  docker exec -i fitcoach-db-prod psql -U fitcoach -d fitcoach
```

---

## 🧯 应急排查

| 现象 | 排查 |
|---|---|
| 页面打不开 | `docker compose ps` 看容器状态 |
| 500 错误 | `docker compose logs --tail=100 backend` 看 traceback |
| 数据库连不上 | `docker compose logs db` + `docker exec fitcoach-db-prod pg_isready` |
| 发消息无响应 | 看 backend 日志有没有 Moonshot API 报错（quota / model 名） |
| 容器重启不停 | 日志 + `docker inspect fitcoach-backend-prod` 看健康检查配置 |

---

## 🔐 服务器 .env.prod 关键字段

路径：`/root/fitcoach/.env.prod`，**只在服务器上维护**，不要用 rsync 覆盖。

```
DATABASE_URL=postgresql+asyncpg://fitcoach:xxx@db:5432/fitcoach
JWT_SECRET=xxx
MOONSHOT_API_KEY=xxx
MOONSHOT_MODEL=kimi-k3
ZHIPU_API_KEY=xxx           # M8 RAG embedding
```

改完要重启后端：
```bash
docker compose -f docker-compose.prod.yml up -d backend
```

---

## 📋 一键发版 cheat sheet

```bash
# 本地
cd /Users/alice/Desktop/fitcoach && \
rsync -avz --delete --exclude '.venv' --exclude 'node_modules' \
  --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude 'dist' --exclude '.env' --exclude '.DS_Store' \
  ./ root@43.137.46.175:/root/fitcoach/

# 服务器
ssh root@43.137.46.175 "cd /root/fitcoach && \
  docker compose -f docker-compose.prod.yml up -d --build backend web && \
  docker compose -f docker-compose.prod.yml ps"
```
