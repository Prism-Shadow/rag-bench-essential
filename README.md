# RAG Bench Essential

本仓库保存当前固定的 15 个数据分析 benchmark case，以及复现官方评分所需的
rubric、gold answer、validator、reference solution 和视觉 judge prompt。其他人可以
只使用本仓库运行并评分自己的 agent。

每个 `cases/<case_id>/` 同时保存两类内容：

- agent 可见的 `task.md`、`data/` 和可选 `env.md`；
- 只供外部评分器使用的 `truth/`，其中包含 rubric、gold、validator、reference
  solution，以及个别 case 的视觉 judge 配置和 prompt。

`truth/` 进入 Git 是为了让 benchmark 可复现，但绝不能复制到被测 agent 的
workspace。`scripts/stage_case.py` 只会复制 `task.md`、`data/` 和 `env.md`。

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

因此 DCI 的 evaluation 包可以审计，但完整运行前仍需按
`cases/dci_browsecomp_architecture_firm_hard/README.md` 从官方来源 materialize payload。

## Quick start

安装评分依赖并拉取 Git LFS 数据：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-eval.txt
git lfs pull
```

为一个 case 创建隔离 workspace：

```bash
python scripts/stage_case.py \
  --case-id prepbench_loyalty_tier_normalization_hard \
  --workspace /tmp/rag-bench/prepbench
```

让自己的 agent 只在该 workspace 中完成 `task.md`，然后从仓库根目录评分：

```bash
python scripts/score_case.py \
  --case-id prepbench_loyalty_tier_normalization_hard \
  --workspace /tmp/rag-bench/prepbench
```

评分报告默认写入 workspace 同级的 `score.json`。DV-World 和 BankerToolBench 的
official PASS 还要求视觉 judge；确定性评分通过后，可设置
`BENCH_VISION_JUDGE_MODEL`、`BENCH_VISION_JUDGE_API_KEY` 和可选的
`BENCH_VISION_JUDGE_BASE_URL`，再增加 `--api-vision-judges`。完整 judge prompt 已包含在
对应的 `cases/<case_id>/truth/vision_judge_prompt.md`。评分材料的详细约定见
[`EVALUATION.md`](EVALUATION.md)。

发布或修改 case 后运行仓库完整性检查：

```bash
python scripts/verify_repository.py
```

## Data and Git LFS

LongDA 的大 CSV 和 Spider2-Lite 的 SQLite 文件由 Git LFS 管理。clone 后如未自动
下载，可执行：

```bash
git lfs pull
```

第三方数据仍受各自上游许可证和访问条款约束，详见
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
