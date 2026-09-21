# FitCoach 前端 Docker 镜像
# 多阶段: builder 跑 vite build,runtime 只做静态文件源(交给 Caddy)
# 也可以让 Caddy 直接挂载 dist/,但打成镜像方便部署一致性

FROM node:22-alpine AS builder

WORKDIR /app

# 先拷贝 lockfile 装依赖,缓存友好
COPY package.json package-lock.json ./
RUN npm ci

# 拷业务代码 + 构建配置
COPY tsconfig*.json vite.config.ts index.html ./
COPY src ./src

# 构建产物落在 /app/dist
RUN npm run build

# ============================================================
# runtime 阶段用 caddy 直接托管静态文件(2MB 极小镜像)
FROM caddy:2-alpine

# 覆盖默认 Caddyfile,后续可以用 volume 挂载真的 Caddyfile
COPY --from=builder /app/dist /srv

# 默认 Caddyfile: 提供静态文件 + SPA fallback
RUN echo ':80 { \n\
    root * /srv \n\
    file_server \n\
    try_files {path} /index.html \n\
}' > /etc/caddy/Caddyfile

EXPOSE 80
