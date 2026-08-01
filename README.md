# RAG Bench Essential

本仓库保存当前固定的 15 个数据分析 benchmark case 的 agent 可见内容。

每个普通 case 位于 `cases/<case_id>/`，包含：

- `task.md`：任务描述与最终交付要求；
- `data/`：任务输入数据；
- 可选的 `env.md`：运行环境假设。

本仓库不包含 gold answer、rubric、validator、reference solution、历史运行结果或
agent trace。评分内容与 agent workspace 分离，避免 benchmark 泄漏。

## Fixed 15

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
15. `fdabench_app_sentiment_xsource_hard_v2`

## DCI case

BrowseComp-Plus / DCI 的明文任务、ground truth 和 materialized corpus 不上传 Git。
仓库仅保留来源和本地 materialization 说明；授权用户需要通过官方分发渠道获取数据。

## Data and Git LFS

LongDA 的大 CSV 和 Spider2-Lite 的 SQLite 文件由 Git LFS 管理。clone 后如未自动
下载，可执行：

```bash
git lfs pull
```

第三方数据仍受各自上游许可证和访问条款约束，详见
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
