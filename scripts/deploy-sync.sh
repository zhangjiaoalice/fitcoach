#!/usr/bin/env bash
set -euo pipefail # 前面哪一步失败了就不回再跑了
# ============================================================
# 本地代码同步脚本
# 目标服务器 43.137.46.175
# 用法：
    # ./deploy-sync.sh # 真的同步
    # ./deploy-sync.sh --dry-run # 预览，不改动
# ============================================================

REMOTE_USER="root"
REMOTE_HOST="43.137.46.175"
REMOTE_PATH="/root/fitcoach/"
LOCAL_PATH="/Users/alice/Desktop/fitcoach/"

# 彩色输出变量
RED='\033[0;31m'
GREEN='\033[0;32m'
RESET='\033[0m'

# ─── 参数解析 ────────────────────────────────────
# 从命令行读取参数，识别是否传入了 --dry-run
# [[...]] bash 条件测试语法
DRY_RUN=""
# 只要还有参数没处理完（$# > 0），就继续循环。每处理一个参数，参数（$#）个数会减少，循环最终自然结束
while [[ $# -gt 0 ]]; do case $1 in --dry-run) DRY_RUN="--dry-run"; shift ;; *) break ;; esac; done

# ─── 前置检查 ────────────────────────────────────
# 确认 LOCAL_PATH 存在而且是目录
if [ ! -d "$LOCAL_PATH" ]; then
    echo -e "${RED}错误：${LOCAL_PATH} 不存在${RESET}"
    exit 1
fi
# 确认当前 git 分支（可选但有用）, 如果不存在，警告但是可以继续进行
BRANCH=$(git -C "$LOCAL_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "non-git")
DIRTY=$(git -C "$LOCAL_PATH" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
echo -e "${GREEN}📦 当前分支: ${BRANCH}  未提交改动: ${DIRTY} 个文件${RESET}"

# SSH 握手检测，如果失败，提前告知用户
ssh -o BatchMode=yes -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" true

# ─── 排除清单 ────────────────────────────────────
# 将要排除的目录/文件写成数组，循环拼成 --exclude 参数
# 必须要排除的文件 .env node_modules dist .git __pycache__ ‘*.pyc’ .env.prod .DS_Store .pytest_cache .mypy_cache logs
EXCLUDES_FILE=(.env node_modules dist .git __pycache__ '*.pyc' .env.prod .DS_Store .pytest_cache .mypy_cache logs)

# 把排除清单拼成 rsync 的参数数组
RSYNC_EXCLUDES=()
for e in "${EXCLUDES_FILE[@]}"; do
    RSYNC_EXCLUDES+=(--exclude "$e")
done


echo "⚠️  以下文件/目录会被排除同步，确保服务器端已有正确版本："
printf '    %s\n' "${EXCLUDES_FILE[@]}"

# ─── 执行同步 ────────────────────────────────────
# 组装并执行 rsync 命令
if rsync -avzP $DRY_RUN --delete "${RSYNC_EXCLUDES[@]}" "$LOCAL_PATH" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"; then
    echo -e "${GREEN}✅ 同步完成${RESET}"
else
    echo -e "${RED}❌ 同步失败${RESET}"
    exit 1
fi

# ─── 远程重建容器 ────────────────────────────────────
if [ -z "$DRY_RUN" ]; then
    echo -e "${GREEN}🚀 远程重建容器...${RESET}"
    ssh "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_PATH && \
        docker compose -f docker-compose.prod.yml up -d --build backend web && \
        docker compose -f docker-compose.prod.yml ps"
fi