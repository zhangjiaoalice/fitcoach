# STAR 01 · Kimi 返回 arguments 的"拼接格式" × 可观测性的真实价值

> **一句话复述**：评估脚本加了 traceback 后通过率反而掉了 20 个百分点——因为之前的 except 吞异常让假阳性遮蔽了真失败。定位到 LLM provider 层面的 JSON 拼接陷阱，改完顺带治好了生产的 silent bug。
>
> **讲完大约 4 分钟**。适合被问"你怎么保证 Agent 稳定" / "有没有踩过 LLM provider 的坑" / "怎么做可观测性"。

---

## 💡 本故事核心价值（在答辩时隐含呈现的"我"）

- **用数据驱动决策**：改动不靠感觉，每轮通过率都归因清楚
- **优先解决观测能力**：加 traceback 是看似退步（通过率掉）但真正进步（真实暴露 bug）
- **顺带治生产 bug**：评估跑的是 `run_agent`（同步），但找到的 bug 流式路径 `run_agent_stream` 也有，一起修
- **明确 LLM 不可控 vs 可控的边界**：剩下 1 条失败承认是 provider 层随机性，不虚张

---

## S — Situation（背景 · 30 秒）

FitCoach 的 Agent 用 Moonshot Kimi K3 做 function calling，9 个工具覆盖记录 + 查询 + RAG。已经上线跑了一段时间，用户能聊天能记数据，看起来一切正常。

但面试被追问"你怎么知道 Momo 回答得好不好"的时候，我意识到当前只有**人工眼看 trace**——没有自动评估、没有数字。所以我决定做一个评估脚本。

---

## T — Task（目标 · 20 秒）

- 20 条 YAML golden set 覆盖**工具调用 / 安全召回 / RAG 相关性**三维度
- Runner 自动跑 → 输出 JSON + Markdown 报告
- 要能回答一个具体问题："当前通过率是多少？"

---

## A — Action（动作 · 2 分钟）

### 第一轮（65%）

脚本写完直接跑 20 条：

```
tool_call: 9/11 (82%)
safety:    3/5  (60%)
rag:       1/4  (25%)
总体:      13/20 (65%)
```

看着还行，RAG 25% 略低但知识库只有 9 段，情有可原。

**但我注意到几条 runtime error 的 reason 只写 `Extra data: line 1 column 3`**，看不出栈。因为当时 runner 的 except 是这样写的：

```python
except Exception as e:
    results.append({"reasons": [f"RUNTIME ERROR: {e}"]})
```

**只保留了异常消息，丢了 traceback**——定位不到是哪个文件哪一行炸了。

### 第二轮（45%，看似退步）

加上 `traceback.format_exc()`：

```python
except Exception as e:
    tb = traceback.format_exc()
    results.append({"reasons": [f"RUNTIME ERROR: {e}\n{tb[:500]}"]})
```

重跑，**通过率反而掉到 45%**。

同事可能会慌，但我知道这是好事——**之前 65% 里有一部分是"异常被吞的假阳性"**。现在真实失败全暴露，我终于看到栈顶在哪：

```
File "app/agent/loop.py", line 129, in run
    arguments = json.loads(call["function"]["arguments"])
json.decoder.JSONDecodeError: Extra data: line 1 column 3 (char 2)
```

### 定位根因

`Extra data: line 1 column 3` 的典型场景是什么？`json.loads` 读完一个 JSON 对象后发现**字符串里还有残余**。

比如 `'{}{"ml":500}'`——`json.loads` 读到第一个 `{}` 就停，`char 2` 的 `{` 被当成 extra data。

我本地写了个最小复现：

```python
>>> json.loads('{}{"ml":500}')
json.decoder.JSONDecodeError: Extra data: line 1 column 3 (char 2)
```

**一行对上**。说明 Kimi 偶发返回的 tool arguments 不是单一 JSON 对象，而是"**前导空 `{}` + 真 args**"的拼接格式。

### 修复设计

直接 catch 并 fallback 到空字典吗？**不行**——那会导致工具用空参数调用，比如 `log_water(ml=None)` 直接炸。生产环境的 `run_agent_stream` 就是这么做的，等于把"参数解析失败"掩盖成了"工具调用用空参数"的 silent bug。

改用 `json.JSONDecoder().raw_decode()`：**逐段扫描，优先返回第一个非空字典**：

```python
def _parse_tool_arguments(fn_name, raw):
    text = (raw or "").strip()
    dec = json.JSONDecoder()
    pos = 0
    first_obj = None
    while pos < len(text):
        while pos < len(text) and text[pos] not in "{[":
            pos += 1
        if pos >= len(text): break
        try:
            obj, consumed = dec.raw_decode(text[pos:])
        except json.JSONDecodeError:
            pos += 1
            continue
        pos += consumed
        if isinstance(obj, dict):
            if obj:  # 非空字典直接返回
                return obj
            if first_obj is None:
                first_obj = obj
    return first_obj if first_obj is not None else {}
```

验证 9 条边界 case 全对：

```
'{"ml":500}'                   → {"ml": 500}
'{}{"ml":500}'                 → {"ml": 500}    ← 关键 case
'{"ml":500}{}'                 → {"ml": 500}
'{"ml":500}trailing'           → {"ml": 500}
''                             → {}
None                           → {}
```

**顺带把 `run_agent_stream` 流式路径也用这个 helper 替换**——它之前 silent fallback 到 `{}` 的 bug 一起修了。这是本次改动隐藏的 ROI。

### 第三轮（80%）、第四轮（95%）

改完 loop.py，第三轮 **80%**（+35 个百分点）。

剩下的失败里有 2 条是"LLM 跑满 5 轮没出结果"——不是 bug，是 `max_iterations=5` 太激进。调到 8 + 把一条和产品行为冲突的 case 改成"期望追问"而非"期望工具调用"（Agent 遵守"信息不够先追问"的设计原则），第四轮 **95%（19/20）**。

---

## R — Result（结果 · 30 秒）

### 直接产出

- 总体通过率 **65% → 45% → 80% → 95%**
- 4 轮迭代每次都有具体可归因改动
- 评估报告里有完整失败 case 明细 + traceback
- Kimi tool_call JSON 解析 bug 定位 + 修复 + 覆盖同步/流式两条路径

### 更深的收获

1. **观测能力 > 测试数量**：加 traceback 让通过率"短期退步"，但真实暴露了被吞掉的 bug——这是正收益
2. **评估驱动找出生产 bug**：测试工具跑的是 `run_agent`，但发现的 bug 在生产走的 `run_agent_stream` 里一样存在
3. **知道 LLM 的不可控边界**：剩下 1 条 Kimi 偶发"假装调过工具"的 case 承认是 provider 层随机性，没强行把分数推到 100%

### 如果再做一次会怎么调

- 评估脚本应该一开始就带完整 traceback，别等出错才加
- except Exception 太宽，很多项目都踩过同类坑（我这个项目就在 jose/PyJWT 混用上吃过一次亏）→ 应该默认所有 except 都带 `format_exc()`，发警告或至少 log 级别打出来

---

## 🎤 面试讲稿（30 秒 / 2 分钟 / 4 分钟三版）

### 30 秒版

> 我做了个 Agent 评估脚本，20 条 golden set。首次跑 65%，加完完整 traceback 掉到 45%——因为之前的 except 吞异常让假阳性遮蔽了真失败。从异常栈定位到 Kimi 偶发返回 `'{}{"ml":500}'` 这种拼接 JSON，用 `raw_decode` 逐段扫描优先非空字典修完到 95%。顺带把生产流式路径的同款 silent bug 也治了。

### 2 分钟版

在 30 秒版基础上加：
- 数字曲线：65 → 45 → 80 → 95
- `max_iterations` 的调整和"信息不够先追问"的产品 case 修正
- 结论"观测能力 > 测试数量"

### 4 分钟版

用上面完整的 S/T/A/R 内容。被追问"怎么验证修复"时，拿出 9 条边界 case 单元测试那段。

---

## 🧷 可能被追问的 5 个问题 + 预答

**Q1**: 为什么不直接向 Moonshot 报 bug 让他们修？
**A**: 报了（如果他们愿意修）。但客户端兜底仍然要做，不能假设 provider 永远正确。这是 LLM 工程里的通用原则："把 provider 当成有概率出错的下游依赖"。

**Q2**: 怎么判断是 Kimi 的锅而不是你 Agent 的锅？
**A**: `_parse_tool_arguments` 里 `print` 打印了原始 `raw={raw!r}` 到 stdout，重跑时能看到原始字符串。

**Q3**: `raw_decode` 的性能？
**A**: 调用频次很低（每次 tool call 一次），且输入最大也就几百字符，纳秒级。真正耗时的是 LLM round-trip，这里不是瓶颈。

**Q4**: 为什么选"优先非空字典"而不是"取最后一个"？
**A**: 从实际观察到的 Kimi 行为归纳。拼接格式几乎都是 `前导空{} + 真 args`，没见过反过来。如果以后看到 `真 args + 尾部空{}`，`优先非空`也兼容。

**Q5**: 评估只跑一次能信吗？LLM 有随机性。
**A**: 确实需要跑多次取平均。当前是 `temperature=1`（Kimi K3 不支持别的），确实有波动。下一步想给评估加 N=3 的重复跑 + 统计方差，但现在时间不够，面试里会主动讲这一步。
