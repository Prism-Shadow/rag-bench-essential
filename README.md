# RAG Bench

本仓库保存 15 个 benchmark case、RAG Agent 的 `AGENTS.md`，以及 Original PG Agent、
RAG Agent、Claude Code 和 Codex 的 60 条 trace。

## 内容

- `cases/<case>/task.md`：任务描述。
- `cases/<case>/data/`：任务数据。
- `agent-configs/rag-agent/AGENTS.md`：RAG Agent 指令。
- `agent-configs/original-pg-agent/AGENTS.md`：Original PG Agent 使用的近空指令。
- `traces/<agent>/<case>.jsonl`：四组结果各 15 条 trace。
- `figures/agent_results.png`：总体通过数和逐 case 结果图。

## Results

| Agent | PASS | 说明 |
| --- | ---: | --- |
| Original PG Agent | 3/15 | 使用只有标题的近空 `AGENTS.md` |
| RAG Agent | 10/15 | 使用本仓库 `agent-configs/rag-agent/AGENTS.md` |
| Claude Code | 10/15 | 15 个 case 各选一条 trace |
| Codex | 7/15 | 15 个 case 各选一条 trace |

Original PG Agent 的 15 条 trace 位于 `traces/original-pg-agent/`。其中 13 条来自原始
baseline，当前集合后来加入的 DocFinQA PDF 和 DocVQA OCR 使用相同的近空
`AGENTS.md` 配置补跑。15 个 case 均有可解析 trace；DCI 和 HarveyLab 是异常终止的失败
记录，其余 13 条运行正常结束。更具体的来源和结果见该目录下的 `README.md`。

![15-case agent results](figures/agent_results.png)

## Cases

1. `spider2lite_f1_overtake_audit_hard`
2. `dci_browsecomp_architecture_firm_hard`
3. `docfinqa_oilgas_canada_pdf_hard`
4. `docvqa_contract_effective_date_ocr_hard`
5. `longda_nscg_telework_hard`
6. `multihiertt_global_products_atoi_share_hard`
7. `workspacebench_taobao_permissions_hard`
8. `dvworld_dvevol_crime_association_network_hard`
9. `bankertoolbench_cake_lbo_sensitivity_hard`
10. `finlongdocqa_interest_expense_sensitivity_screen_hard`
11. `dabstep_real_fees_1681`
12. `prepbench_loyalty_tier_normalization_hard`
13. `spreadsheetbench_working_paper_transpose_hard`
14. `harveylab_reps_diligence_discrepancy_hard`
15. `medagentbench_potassium_repletion_order_hard`


DCI/BrowseComp-Plus 的明文任务和语料受上游发布限制，因此该 case 只保留说明，
不上传受限内容。第三方数据权利说明见 `THIRD_PARTY_NOTICES.md`。
