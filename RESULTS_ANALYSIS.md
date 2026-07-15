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

## 时间与 token

下表同时给出按指标过滤后的平均数和中位数。耗时是 trace 首尾时间戳跨度；token 使用跨 runtime
更可比的输出 token。Original PG Agent 的 DCI 只剔除异常 latency，其 8,236 个输出 token
仍计入 token 汇总；Claude Code 的 DocVQA 因 401 没有发生模型调用，两个指标都不计入均值。

| Setting | Latency n | Token n | 平均耗时 | 中位耗时 | 平均输出 token | 中位输出 token |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Original PG Agent | 14 | 15 | 6m 47s | 5m 10s | 16.1K | 12.2K |
| RAG Agent | 15 | 15 | 9m 01s | 6m 25s | 21.1K | 19.4K |
| Claude Code | 14 | 14 | 10m 12s | 5m 53s | 27.7K | 18.6K |
| Codex | 15 | 15 | 4m 00s | 3m 56s | 13.7K | 15.6K |

按 case 看，DCI 和 BankerToolBench 的平均耗时分别为 22.8 和 21.1 分钟，明显高于其他
case。BankerToolBench 还需要平均 44.9K 输出 token，反映其 Excel、PPT、PDF 多交付链路；
DCI 的高耗时则主要来自大语料搜索和收束困难。DocFinQA 和 MedAgentBench 的平均耗时
分别为 1.9 和 2.1 分钟。

RAG Agent 与 Claude Code 都通过 10/15；RAG Agent 的平均耗时和输出 token 分别为
9.0 分钟和 21.1K，低于 Claude Code 的 10.2 分钟和 27.7K。Codex 更快、输出更少，
但只通过 7/15，因此不能把较低时间或 token 直接解释为更高效率。逐 trace
原始值和逐 case 稳健汇总见 [`results/`](results/README.md)。
