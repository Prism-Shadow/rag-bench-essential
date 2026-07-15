# RAG Bench Essential

这个仓库保存 Agentic RAG BenchLab 当前固化的 15 个主代表 case，以及 RAG Agent 使用的专用 `AGENTS.md`。

当前已加入 PG Agent v1.14 的 15-case 选定 result/trace 包；CC 和 Codex 的
result/trace 仍待单独清理和校验后加入。

## 目录

- `cases/`：15 个固定 case。
- `agent-configs/rag-agent/AGENTS.md`：RAG Agent 使用的专用指令，不是项目根目录的开发指南。
- `outputs/pg-dsv4pro-v114-selected-20260715/`：v1.14 的 15 条选定 trace、validator log、artifact manifest 和机器可读索引。
- `CASE_SPEC.md`：case 的 `payload + env + eval` 结构规范。
- `RUN_PROTOCOL.md`：不暴露 `truth/` 的隔离运行和外部验证流程。
- `THIRD_PARTY_NOTICES.md`：第三方 benchmark 数据说明。

## 15 个主代表 case

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

## 数据说明

普通 case 的 payload 和外部 validator 一起保存。两个较大文件通过 Git LFS 管理：

- `cases/longda_nscg_telework_hard/data/epcg23.csv`
- `cases/spider2lite_f1_overtake_audit_hard/data/f1.sqlite`

clone 后运行 `git lfs pull` 获取完整 payload。

DCI/BrowseComp-Plus 的明文 task、truth 和 corpus 受上游发布约束，本仓库只保存受限 case 占位和数据获取说明，不上传明文。

## 运行边界

不要直接在 `cases/` 中运行 Agent。运行时应将 `task.md`、`data/` 和可选 `env.md` 复制到独立 workspace；`truth/` 只供 workspace 外部的 validator 使用。

## PG v1.14 结果

`outputs/pg-dsv4pro-v114-selected-20260715/` 覆盖 15/15 case，择优重试后
PASS 10/15，与当前 CC canonical 的 PASS 数量和集合相同。它不是一次
single-shot full batch；Spider2-Lite、MultiHiertt 和 MedAgentBench 的重试
边界以及 MedAgentBench 的 artifact-only validator 口径都在结果包的
`README.md` 和 `manifest.tsv` 中明确记录。
