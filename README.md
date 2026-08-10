# RAG Bench Essential

[Project website](https://prism-shadow.github.io/rag-bench-essential/) · [Evaluation contract](EVALUATION.md)

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

## Results

每个 setting 保留一轮完整的 15-case 结果。Accuracy 按 official hard PASS 统计；时间为每题平均值，Token 和成本为完整一轮的合计。

| Setting | 版本与配置 | Gemini 视觉 | Accuracy | Avg. time / case (min) | Total tokens (M/run) | Total cost (USD/run) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Penguin w/o Skill | PenguinHarness v0.0.1 / DeepSeek V4 Flash xhigh / no skill / Goal off | 允许 | 8/15（53.3%） | 9.10 | 18.51 | $0.2407 |
| Penguin w/o Skill | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / no skill / Goal off | 允许 | 9/15（60.0%） | 5.99 | 17.78 | $0.2231 |
| Penguin w/ Auto-optimized Agent State | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / one-round auto-optimized Agent State / Goal off | 允许 | 10/15（66.7%） | 6.29 | 13.75 | $0.2158 |
| Penguin w/ Manual Skill | PenguinHarness v0.0.1 / DeepSeek V4 Flash xhigh / manual Skill / Goal off | 允许 | 9/15（60.0%） | 6.51 | 16.44 | $0.2250 |
| Penguin w/ Manual Skill | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / manual Skill / Goal off | 允许 | 11/15（73.3%） | 6.52 | 12.38 | $0.1995 |
| Penguin w/ Manual Skill + Goal | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / manual Skill / Goal on | 允许 | 11/15（73.3%） | 5.84 | 17.65 | $0.2267 |
| Claude Code | Claude Code CLI 2.1.191 / Claude Opus 4.8 / effort=max | 不允许 | 10/15（66.7%） | 10.61 | 16.93 | $34.27 |
| Codex | Codex CLI 0.146.0-alpha.9.2 / GPT-5.5 xhigh / no skill | 不允许 | 10/15（66.7%） | 7.26 | 12.22 | $18.94 |

2026-08-10 修正 BankerToolBench 的 workbook locator 后，Claude Code 的既有产物从
FAIL 重评为 PASS（视觉 verdict 与产物 SHA 绑定且仍有效），因此由 9/15 更新为
10/15。其余七个 setting 未保留该 case 的 workspace 产物，无法按新 evaluator
重评；表中暂保留其历史结果，不据此猜测增减。

## DCI case

BrowseComp-Plus / DCI 的 canonical task 已包含在仓库中，大 corpus 不上传 Git。完整运行前按
[`cases/dci_browsecomp_architecture_firm_hard/README.md`](cases/dci_browsecomp_architecture_firm_hard/README.md)
从 Hugging Face 官方数据集一键 materialize payload。

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
