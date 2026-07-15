# Trace metrics

本目录保存 60 条 selected trace 的时间与 token 统计。

- `trace_metrics.csv`：逐 trace 明细，共 60 行，包含结果、起止时间、耗时、token 分量、运行状态和异常值标记。
- `case_summary.csv`：逐 case 汇总，共 15 行；对四个 setting 取稳健中位数。
- `setting_summary.csv`：逐 setting 汇总，共 4 行；同时保留原始总耗时和剔除异常后的统计。

## 统计口径

- 耗时是 trace 中第一条到最后一条可解析时间戳的跨度，不包含外部 validator。
- 跨 runtime 比较使用 `output_tokens`。`processed_tokens` 保留各 runtime 原生上报值，但输入和 cache 语义并不完全一致。
- PG 使用最后一条累计 `token_usage.session`；Claude Code 按 API message id 去重后求和；Codex 使用最后一条累计 `total_token_usage`。
- Setting 和 case 的稳健值均使用中位数。

两条明确的执行异常不进入稳健汇总：

| Setting | Case | 原因 |
| --- | --- | --- |
| Original PG Agent | DCI / BrowseComp+ | 命令长时间停滞后终止，trace 跨度约 7 小时 50 分钟。 |
| Claude Code | DocVQA | 401 runtime error，没有产生模型 token。 |

Original PG Agent 的 HarveyLab 在 agent 运行后出现 protocol error，`trace_status` 已标记；其时间和 token 仍完整且数值不异常，因此保留在汇总中。

重新生成 CSV 和图：

```bash
python3 figures/plot_trace_efficiency.py
```
