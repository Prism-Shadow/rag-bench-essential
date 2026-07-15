# Trace metrics

本目录保存 60 条 selected trace 的时间与 token 统计。

- `trace_metrics.csv`：逐 trace 明细，共 60 行，包含结果、起止时间、耗时、token 分量、运行状态，以及 latency/token 各自的有效性标记。
- `setting_summary.csv`：四个 harness/configuration 的汇总；分别按有效 latency 和有效 token 计算 clean mean 与中位数。

## 统计口径

- 耗时是 trace 中第一条到最后一条可解析时间戳的跨度，不包含外部 validator。
- 跨 runtime 比较使用 `output_tokens`。`processed_tokens` 保留各 runtime 原生上报值，但输入和 cache 语义并不完全一致。
- PG 使用最后一条累计 `token_usage.session`；Claude Code 按 API message id 去重后求和；Codex 使用最后一条累计 `total_token_usage`。
- latency 和 token 独立过滤，不会因为某条 trace 的耗时异常就丢掉其有效 token。
- Harness/configuration 汇总同时提供各指标的 clean mean 与中位数；主图展示均值。

指标级有效性如下：

| Setting | Case | Latency | Token | 原因 |
| --- | --- | --- | --- | --- |
| Original PG Agent | DCI / BrowseComp+ | 剔除 | 保留 | 命令长时间停滞后终止，墙钟跨度异常；已产生的 8,236 个输出 token 仍是有效观测。 |
| Claude Code | DocVQA | 剔除 | 剔除 | 401 runtime error，没有发生模型调用；原始 0 token 仍保留在明细中。 |

Original PG Agent 的 HarveyLab 在 agent 运行后出现 protocol error，`trace_status` 已标记；其时间和 token 仍完整且数值不异常，因此保留在汇总中。

重新生成 CSV 和图：

```bash
python3 figures/plot_trace_efficiency.py
```
