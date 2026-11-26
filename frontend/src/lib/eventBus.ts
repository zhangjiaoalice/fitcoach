/**
 * 应用级事件总线（极简发布订阅）
 *
 * 设计原则：
 *   - 只处理「事件」(fire-and-forget)，不存储状态；状态走各 view 自己
 *   - 事件名用字符串字面量联合类型，编译期防拼错
 *   - on() 返回 unsubscribe 函数，配合 onBeforeUnmount 防泄漏
 *
 * 当前事件：
 *   - "data-changed"：Agent 工具落库后触发，payload.scope 标识哪些数据变了
 *
 * 为什么不用 Pinia / WebSocket：
 *   - Pinia 杀鸡用牛刀 —— 我们只是传"事件"不是存"状态"
 *   - 这是前端自消化的事件，不是跨用户实时推送，不需要 WS 长连
 */

// ─────────────────────────── 事件类型定义 ───────────────────────────

/** 可变数据域：订阅方据此决定要不要刷新哪块 */
export type DataScope = "diet" | "water" | "workout" | "weight";

export interface DataChangedPayload {
  /** 哪些数据变了（一次可带多个） */
  scope: DataScope[];
  /** 触发来源，调试用，如 "agent:log_diet" / "manual:diet-form" */
  source: string;
}

/** 事件名 → payload 类型的映射。加新事件在这里扩字段 */
export interface AppEvents {
  "data-changed": DataChangedPayload;
}

// ─────────────────────────── 内部实现 ───────────────────────────

type Handler<T> = (payload: T) => void;

// 事件 → handlers 集合
const bus = new Map<keyof AppEvents, Set<Handler<unknown>>>();

// ─────────────────────────── 对外 API ───────────────────────────

/**
 * 发布事件。
 * @example
 *   emit("data-changed", { scope: ["diet"], source: "agent:log_diet" });
 */
export function emit<K extends keyof AppEvents>(
  event: K,
  payload: AppEvents[K],
): void {
  const handlers = bus.get(event);
  if (!handlers || handlers.size === 0) return;

  // 复制一份快照迭代，避免 handler 内部 off() 搞乱当前轮
  [...handlers].forEach((h) => {
    try {
      (h as Handler<AppEvents[K]>)(payload);
    } catch (e) {
      // 一个 handler 炸不影响其他 handler
      console.error(`[eventBus] handler of "${event}" threw:`, e);
    }
  });
}

/**
 * 订阅事件，返回 unsubscribe 函数。
 * @example
 *   const off = on("data-changed", (payload) => { ... });
 *   onBeforeUnmount(off);
 */
export function on<K extends keyof AppEvents>(
  event: K,
  handler: Handler<AppEvents[K]>,
): () => void {
  if (!bus.has(event)) bus.set(event, new Set());
  const set = bus.get(event)!;
  set.add(handler as Handler<unknown>);
  return () => {
    set.delete(handler as Handler<unknown>);
  };
}
