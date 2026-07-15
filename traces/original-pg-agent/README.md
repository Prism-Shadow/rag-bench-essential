# Original PG Agent traces

本目录保存 Original PG Agent 在当前 15 个 benchmark case 上的 15 条 trace。运行时使用
`agent-configs/original-pg-agent/AGENTS.md`，其内容只有 `# AGENTS.md` 标题。

- PASS：5/15（DocFinQA、LongDA、MultiHiertt、BankerToolBench、DABstep）。
- FAIL：10/15。
- 15 条 trace 全部对应仓库当前的 `task.md`。
- Spider2-Lite、LongDA、MultiHiertt、MedAgentBench 和 DVWorld 是本轮重新运行的 5 个 case。
- 所有 15 个 JSONL 文件均非空且可解析；DCI 以 `pg_exit=143` 终止，HarveyLab 以
  `protocol_json_error` 终止，因此这两条是异常终止的完整失败记录，不是正常完成的运行。

这组结果用于展示近空 `AGENTS.md` 下的实测起点。
