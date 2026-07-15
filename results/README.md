# Results

本目录保存三个 Agent 在 15 个固定 case 上的选定代表结果，共 45 条 trace。

| Agent | Coverage | PASS |
| --- | ---: | ---: |
| RAG Agent | 15/15 | 10/15 |
| Claude Code | 15/15 | 10/15 |
| Codex | 15/15 | 7/15 |

每个 Agent 目录包含：

- `traces/<case>.jsonl`：完整运行 trace。
- `validation/<case>.txt`：workspace 外部 validator 的原始输出。

`manifest.tsv` 是统一索引，`SHA256SUMS` 用于校验文件完整性。

这些 trace 是各 Agent 的选定代表结果，不主张来自同一次连续批量运行。
公开路径只使用稳定的 Agent 和 case 名称；原始 trace 内部的运行时间等历史
元数据保持原样，未做改写。
