# 结果分析

Original PG Agent 使用近空 `AGENTS.md`，通过 5/15；RAG Agent 通过 10/15。Trace 显示，
差距主要出现在检索之后：如何固定计算口径、绑定证据，以及把结果完整交付。

## `AGENTS.md` 带来了什么

- **完整交付。** Spider2-Lite 中，近空配置算对了三部分答案，但 `evidence.json` 没有完整说明
  R/P/S/T 分类含义，最终仍为 FAIL；RAG Agent 同时交付了正确答案和完整证据。
- **固定计算口径。** PrepBench 需要先规范化会员等级，再严格执行利润公式。RAG Agent 保留关键
  中间量并得到正确结果，避免了“数据找对、公式实现却偏掉”。
- **先探测再处理。** SpreadsheetBench 中，RAG Agent 先检查 sheet、重复区块和锚点，再生成并
  验证三个 workbook，减少了根据局部内容猜测表格结构的问题。

其中 Spider2-Lite 是本次同任务重跑中最直接的对照。LongDA 和 MultiHiertt 在当前同一版题目下，
近空配置和 RAG Agent 都通过，因此这两个 case 没有体现出 `AGENTS.md` 带来的结果差异。

## 仍未通过的 5 个 case

| Case | 失败点 | 具体表现 |
| --- | --- | --- |
| DCI / BrowseComp+ | 长任务收束 | 找到强候选后仍继续搜索，三个结果文件均未交付。 |
| DocVQA | OCR 证据绑定 | 输出 `2-7-39`，正确日期为 `7-1-99`。 |
| WorkspaceBench | 业务规则执行 | 文件齐全，但权限矩阵为 38/45，规则为 6/9。 |
| DVWorld | 数据清洗边界 | 扩大了 `Area` 的匹配范围，导致相关系数边表整体偏离。 |
| FinLongDocQA | 入选条件绑定 | 错误排除 CL 和 STZ，进而影响排序和最终 spread。 |

当前剩余问题集中在任务收束、证据绑定和规则边界，而不是基础文件检索。

## Harness 对 latency、token 和 cost 的影响

Original PG Agent 的 DCI 只剔除异常 latency，其有效 token 仍保留；Claude Code 的 DocVQA
因 401 没有发生模型调用，因此从 latency、token 和 cost 均值中剔除。费用按
[DeepSeek V4 Pro 官方价格](https://api-docs.deepseek.com/quick_start/pricing)估算，不代表
实际 provider/relay 账单。

| Harness | PASS | 平均耗时 | 平均总 token | 估算费用/trace |
| --- | ---: | ---: | ---: | ---: |
| Original PG Agent | 5/15 | 6m 47s | 0.72M | $0.0278 |
| RAG Agent | 10/15 | 9m 01s | 1.20M | $0.0368 |
| Claude Code | 10/15 | 10m 12s | 1.51M | $0.0458 |
| Codex | 7/15 | 4m 00s | 0.89M | $0.0285 |

Latency 与 token 的共同驱动因素是模型往返次数。统一比较 14 个有模型调用的 case 时，
Original PG、RAG Agent、Claude Code 和 Codex 分别产生 411、473、515 和 303 次模型调用；
四者工具返回文本总量却很接近，约为 1.40M、1.45M、1.56M 和 1.40M 字符。因此主要差异
不是读取了多少原始数据，而是累计上下文被重新送入模型多少次。

- **Claude Code** 的模型轮数最多、单轮输出也最长，因此 latency、总 token 和费用都最高。
- **RAG Agent** 会继续验证口径、交付物和结果，较 Original PG 多出后期检查轮次；后期上下文
  已经很长，所以模型调用增加 15%，总 processed token 却增加约 46%。这部分开销对应更完整
  的验证和交付，也伴随通过数从 5/15 提升到 10/15。
- **Codex** 用更少的模型轮次批量发出更多工具调用，获得相近工具结果量但减少上下文重放，
  因而最快。它只通过 7/15，说明较低消耗中也包含更早停止或较少复核，不能直接视为更优。

三类 token 中，cache read 占总量的 94% 以上，但官方 cache-hit 单价远低于 uncached input
和 output。因此总 token 与费用并非线性同步：Claude Code 的平均总 token 约为 Original PG
的 2.1 倍，估算费用约为 1.65 倍。逐 trace 原始值和 harness 汇总见
[`results/`](results/README.md)。
