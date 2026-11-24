# FitCoach · AI 健身减脂教练

> 一人全栈独立开发并部署上线的生产级 AI Agent 应用
> 技术栈：FastAPI · PostgreSQL + pgvector · Moonshot Kimi K3 · Vue3 + TS + SSE · Docker Compose
> 代码：[github / 内网仓库链接] · 线上：http://1.13.188.210:8080 （演示账号）

---

## 一句话介绍

一个会"**用工具、查知识、懂边界**"的健身教练对话系统：用户用自然语言记录饮食/训练/体重/饮水/睡眠，Agent 自动调工具落库；要训练建议时，先查用户画像与健康备注，再基于医学指南 RAG 给出不越界的回答。

---

## 核心能力

| 能力 | 技术实现 | 规模 / 评估数字 |
|---|---|---|
| **工具调用** | 自研 Tool Loop + Kimi K3 Function Calling | 9 个 Tool（5 个写 + 4 个读）；工具命中 **91%** |
| **RAG 检索** | pgvector + 智谱 embedding-3（1024 维）+ 余弦相似度 | 9 段医学指南入库；相关性命中 **100%** |
| **流式输出** | SSE（fetch + ReadableStream）+ 前端字符级打字机节流 | 40 字/秒，不掉帧 |
| **Guardrails** | system prompt 边界 + 危机关键词前置拦截 + health_notes 硬约束 | 安全召回 **100%**（5/5 极端场景） |
| **评估体系** | 20 条 YAML golden set + runner 自动跑 + MD/JSON 报告 | **总体 95%**，4 轮迭代归因 |
| **可观测** | `agent_traces` 表记录每轮 iterations / tool_calls / error / latency + eval 报告 traceback | — |
| **鉴权** | PyJWT + 中间件 + 前端过期自动跳登录 | 握手 + 流中双层 401 兜底 |

---

## 技术权衡（有意识的"不选"）

| 没选什么 | 为什么 | 换什么时才切换 |
|---|---|---|
| LangGraph | 场景单轮 1-2 次工具调用，手写 while loop 更可控、方便 debug | 多步回溯、分支/并行、人类介入（Human-in-the-Loop）时 |
| Pinecone / Qdrant | 多一个外部依赖、多一套鉴权，pgvector 单表就够 | 向量 > 100 万或要混合检索（向量+关键字）时 |
| python-jose | 和 PyJWT 两个库异常类型不互认，踩过混用坑；统一 PyJWT | — |
| WebSocket | SSE 单向够用，原生 HTTP 友好代理 | 需双向推送（打断/多人协作）时 |
| Session | JWT 无状态，backend 容器可横向扩展 | 需要服务端主动失效（后台强制下线）时 |
| 原生 PNG | AI 生图默认 1024px，2.4MB 拖慢 LCP | 已改 WebP + preload，体积降 93% |

---

## 架构一览

```
          浏览器 Vue3+TS           Caddy (反代)          FastAPI (async)
          ──────────────           ────────────          ────────────────
          · SSE 消费层             · SPA fallback        · JWT 中间件
          · 打字机节流             · gzip/缓存           · 路由 + 守卫
          · 吉祥物组件 (WebP)                            │
                                                         ▼
                                                   Agent Tool Loop
                                                   ┌───────────────┐
                                                   │ system prompt │
                                                   │ + 用户消息     │
                                                   └──────┬────────┘
                                                          ▼
                                            ┌─────────────────────────┐
                                            │ Moonshot Kimi K3 (LLM)  │
                                            │ Function Calling 决策    │
                                            └──────┬──────────────────┘
                                                   ▼
                              ┌────────── 9 Tools ──────────┐
                              │ CRUD: log_* / query_*       │
                              │ RAG : search_knowledge       │
                              │ Profile: query_user_profile  │
                              └──────┬──────────────────────┘
                                     ▼
                     ┌──────────────────────────────────┐
                     │  PostgreSQL + pgvector            │
                     │  业务表 / 向量表 / agent_traces    │
                     └──────────────────────────────────┘
```

---

## 工程亮点（面试可深入的点）

1. **Guardrails 三层设计**：关键词前置拦 → system prompt 医疗红线 → 工具层参数校验。没把安全全押在 LLM 上。
2. **health_notes 硬约束**：画像里的禁忌（低血糖、膝伤…）每次给建议前强制调 `query_user_profile`，避免"忘了"。
3. **流式 + 打字机解耦**：后端 chunk 推进来是 5-20 字/帧，前端队列化按字节拆单字塞，兼顾真实流式和视觉平顺。
4. **错误分层**：401 走登录跳转 / 400 原地提示 / 500 吐 trace id。排查过 "PyJWT 异常被 jose except 漏掉变 500" 的真实事故。
5. **可量化的质量门**：20 条 YAML golden set + runner 自动跑，通过率从首轮 65% 迭代到 95%；4 轮每一次改动都有具体归因。
6. **容错的 tool-call JSON 解析**：Kimi 偶发返回拼接格式 `'{}{"ml":500}'` 让 `json.loads` 挂；用 `JSONDecoder.raw_decode` 逐段扫描优先非空字典。eval traceback 把这个隐藏 bug 从 45% 的假阳性中扒出来的。

---

## 规模与状态

- **代码体量**：backend ~6000 行 · frontend 15 个 view + 组件库
- **部署**：腾讯云 CVM + 3 容器 Docker Compose（db / backend / web）+ 每日 pg_dump 自动备份
- **已上线**：首页 / 聊天 / 记录 tab / 画像 / Onboarding；工具栏快捷录入；吉祥物 Momo & Hero 双角色
- **性能**：首屏 LCP < 1s（WebP 优化后），对话首 token < 2s

---

## 下一步路线图

| 优先级 | 待做 | 价值 |
|---|---|---|
| P0 | 自动化评估（Ragas / LLM-as-judge）跑 20 条 golden set | 让"工具命中率"有数字 |
| P0 | LangGraph 分支版 Agent，和手写版共存 | 展示对框架的判断力 |
| P1 | Rerank 层（bge-reranker）| RAG top-3 → top-1 精度提升 |
| P1 | 多模型 Router（Kimi/GPT/Claude 可切换）| 规避 provider lock-in + 成本优化 |
| P2 | 用户 👍/👎 反馈 + 进 trace 做 fine-tune 数据 | 数据飞轮 |

---

## 关键技术踩坑故事（面试可展开讲）

1. PyJWT vs python-jose 混用：异常类型族互不认导致 401 被包成 500
2. Docker builder 漏 `COPY public`：图片被 SPA fallback 变 457B HTML
3. Vite PNG 2.4MB → WebP 480KB：PIL 批量压缩 + `<picture>` + preload
4. Kimi K3 不支持 `temperature` 参数：参数剥离兼容
5. Vue proxy 响应式失败：流式打字机不动，改走 `messages[length-1]`
6. health_notes 作为 system prompt 动态注入：而不是让 LLM 自己"记住"
7. **Kimi 返回 tool arguments 偶发拼接格式**：eval runner 加 traceback 后通过率反而掉到 45%，从异常栈里扒出来是 `json.loads` 的锅——改 `raw_decode` 到 95%。观测能力的价值。

---

## 关于我

Alice · 4 年前端工程师 · 近 1 年全栈转型做 AI 应用
邮箱 / 微信 / GitHub
