/**
 * mock 数据 —— M6 联调时逐页替换成真实 API。
 * 保留原样，仅补类型标注，让 IDE 提示更准。
 */

export interface WeightTrendPoint {
  date: string;
  v: number;
}

export interface DashboardData {
  currentWeight: number;
  targetGap: number;
  intakeToday: number;
  intakeRemain: number;
  workoutDone: number;
  workoutPlanned: number;
  weightTrend: WeightTrendPoint[];
  aiTip: string;
}

export interface DietMockLog {
  id: number;
  name: string;
  meal: string;
  time: string;
  kcal: number;
  icon: string;
  color: string;
}

export interface ProfileMock {
  name: string;
  initials: string;
  dayCount: number;
}

export interface PlanRow {
  day: string;
  title: string;
  tag: string;
}

export interface PlanBlock {
  goal: string;
  rows: PlanRow[];
}

export interface ChatMessage {
  type: "user" | "assistant" | "tool" | "citation" | "risk";
  text?: string;
  label?: string;
  status?: string;
  tone?: string;
  plan?: PlanBlock;
}

export const profile: ProfileMock = {
  name: "FitCoach",
  initials: "FC",
  dayCount: 12,
};

export const dashboard: DashboardData = {
  currentWeight: 67.8,
  targetGap: 7.8,
  intakeToday: 1240,
  intakeRemain: 560,
  workoutDone: 2,
  workoutPlanned: 3,
  weightTrend: [
    { date: "7/29", v: 68.6 },
    { date: "7/30", v: 68.4 },
    { date: "7/31", v: 68.5 },
    { date: "8/1", v: 68.1 },
    { date: "8/2", v: 68.2 },
    { date: "8/3", v: 67.9 },
    { date: "今天", v: 67.8 },
  ],
  aiTip: "昨天摄入偏低，今天记得补充优质蛋白，别饿过头影响代谢。",
};

export const dietLogs: DietMockLog[] = [
  { id: 1, name: "燕麦 + 水煮蛋", meal: "早餐", time: "08:10", kcal: 320, icon: "clock", color: "var(--warn)" },
  { id: 2, name: "鸡胸肉 150g + 米饭", meal: "午餐", time: "12:30", kcal: 480, icon: "fork", color: "var(--coral)" },
  { id: 3, name: "希腊酸奶", meal: "加餐", time: "15:40", kcal: 140, icon: "cup", color: "var(--info)" },
  { id: 4, name: "三文鱼 + 西兰花", meal: "晚餐", time: "19:00", kcal: 300, icon: "fish", color: "var(--brand-light)" },
];

export const chatThread: ChatMessage[] = [
  { type: "user", text: "帮我制定一周减脂计划" },
  { type: "tool", label: "读取用户画像", status: "完成", tone: "brand" },
  { type: "tool", label: "生成周计划工具", status: "运行中", tone: "info" },
  { type: "citation", label: "引用《减脂基础 · 热量缺口》" },
  {
    type: "assistant",
    text: "根据你的画像（165cm / 68.5kg，目标 60kg，每周 3 练），建议每日热量缺口约 400 kcal，蛋白质 120g。",
    plan: {
      goal: "目标 −0.5kg",
      rows: [
        { day: "一", title: "力量训练 · 45min", tag: "下肢+核心" },
        { day: "三", title: "有氧 · 30min", tag: "慢跑" },
        { day: "五", title: "力量训练 · 45min", tag: "上肢" },
      ],
    },
  },
  { type: "risk", text: "如膝盖不适，请停止下肢训练" },
];
