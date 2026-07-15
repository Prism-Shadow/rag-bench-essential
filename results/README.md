# Trace metrics

本目录保存 60 条 selected trace 的时间与 token 统计。

- `trace_metrics.csv`：逐 trace 明细，共 60 行，包含结果、起止时间、模型/工具调用数、三类 token、估算费用、运行状态，以及 latency/token 各自的有效性标记。
- `setting_summary.csv`：四个 harness/configuration 的汇总；分别按有效 latency 和有效 token 计算 clean mean、中位数与估算费用。

## 统计口径

- 耗时是 trace 中第一条到最后一条可解析时间戳的跨度，不包含外部 validator。
- 总 token 为 `uncached_input_tokens + cache_read_tokens + output_tokens`。输入和 cache 的原生字段语义并不完全一致，因此同时保留三个分量。
- PG 使用最后一条累计 `token_usage.session`；Claude Code 按 API message id 去重后求和；Codex 使用最后一条累计 `total_token_usage`。
- 模型调用数分别按 PG `token_usage`、Claude Code 去重后的真实 assistant message、Codex `token_count` 事件统计；工具调用按各 runtime 的唯一 tool call id 统计。
- latency 和 token 独立过滤，不会因为某条 trace 的耗时异常就丢掉其有效 token。
- Harness/configuration 汇总同时提供各指标的 clean mean 与中位数；主图展示均值。
- 四组 trace 的模型字段均为 `deepseek-v4-pro`。费用使用 [DeepSeek 官方价格](https://api-docs.deepseek.com/quick_start/pricing)估算：uncached input $0.435/M、cache read $0.003625/M、output $0.87/M（查询日期：2026-07-15）。实际 provider/relay 账单可能不同。

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
