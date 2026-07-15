# Original PG Agent traces

本目录保存 Original PG Agent 在当前 15 个 benchmark case 上的 15 条 trace。运行时使用
`agent-configs/original-pg-agent/AGENTS.md`，其内容只有 `# AGENTS.md` 标题。

- PASS：3/15（DocFinQA、BankerToolBench、DABstep）。
- FAIL：12/15。
- 13 条 trace 来自原始 baseline 中与当前 case 集合重合的运行。
- DocFinQA PDF 和 DocVQA OCR 是为补齐当前 15-case 集合而使用相同近空配置补跑的运行。
- 所有 15 个 JSONL 文件均非空且可解析；DCI 以 `pg_exit=143` 终止，HarveyLab 以
  `protocol_json_error` 终止，因此这两条是异常终止的完整失败记录，不是正常完成的运行。

这组结果用于展示原始 PG Agent 的实测起点。它不应被当成严格的单变量 prompt ablation：
后续 RAG Agent 运行还伴随 system prompt、token budget、runner 和 validator 等变化。
