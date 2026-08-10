# Data Analysis Bench：数据分析智能体评测

语言：[English](README.md) | [中文](README.zh.md) | [实验结果](https://prism-shadow.github.io/rag-bench-essential/)

Data Analysis Bench 使用 15 道任务评测数据分析智能体，覆盖长文档、扫描页面、层次表格、电子表格、SQLite 数据库、跨来源工作流、可视化和交付。

仓库保存每个公开任务的 payload，以及复现官方评分所需的 rubric、gold answer、validator、reference solution 和可选的视觉 judge prompt。其他 agent 可以只使用本仓库创建隔离 workspace 并完成评分。

每个 `cases/<case_id>/` 目录包含两类内容：

- agent 可见的 `task.md`、`data/` 和可选的 `env.md`；
- 只供评分器使用的 `truth/`，包含 rubric、gold、validator、reference solution 和可选的视觉 judge 配置。

评分材料进入 Git 是为了保证可复现性，但绝不能复制到被测 agent 的 workspace。`scripts/stage_case.py` 只会复制 `task.md`、`data/` 和 `env.md`。

## Benchmark 任务

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

## 实验结果

每个 setting 保留一轮完整的 15-case 结果。Accuracy 按 PASS 数量统计；时间为每题平均值；Token 为完整一轮的合计。成本明确标为“已记录成本”，因为 Penguin setting 允许使用 `google/gemini-3.6-flash` 处理视觉输入，但没有保留 OpenRouter 视觉代理费用。Claude Code 和 Codex 没有这个辅助视觉工具。

<!-- RESULTS_TABLE_START -->
| Setting | 版本与配置 | Accuracy | 平均单题耗时（分钟） | 总 Token（百万/轮） | 已记录成本（美元/轮） | 结果口径 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Penguin · 手动调优 | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / 手动调优 / Goal 关闭 | 11/15 (73.3%) | 6.52 | 12.38 | $0.1995 | 历史 evaluator |
| Penguin · 手动调优 + Goal | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / 手动调优 / Goal 开启 | 11/15 (73.3%) | 5.84 | 17.65 | $0.2267 | 历史 evaluator |
| Penguin · Agent 自调优 | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / 单轮 Agent 自调优 / Goal 关闭 | 10/15 (66.7%) | 6.29 | 13.75 | $0.2158 | 历史 evaluator |
| Claude Code | Claude Code CLI 2.1.191 / Claude Opus 4.8 / effort=max | 10/15 (66.7%) | 10.61 | 16.93 | $34.27 | 当前 evaluator |
| Codex | Codex CLI 0.146.0-alpha.9.2 / GPT-5.5 xhigh | 10/15 (66.7%) | 7.26 | 12.22 | $18.94 | 历史 evaluator |
| Penguin | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / Goal 关闭 | 9/15 (60.0%) | 5.99 | 17.78 | $0.2231 | 历史 evaluator |
| Penguin · 手动调优 | PenguinHarness v0.0.1 / DeepSeek V4 Flash xhigh / 手动调优 / Goal 关闭 | 9/15 (60.0%) | 6.51 | 16.44 | $0.2250 | 历史 evaluator |
| Penguin | PenguinHarness v0.0.1 / DeepSeek V4 Flash xhigh / Goal 关闭 | 8/15 (53.3%) | 9.10 | 18.51 | $0.2407 | 历史 evaluator |
<!-- RESULTS_TABLE_END -->

Claude Code 的 10/15 已包含 2026-08-10 修复 evaluator 后的 BankerToolBench 重评。原视觉 verdict 与产物 SHA 绑定，因此仍然有效。其余七个 setting 没有保留重评所需的 workspace 产物，所以结果明确标记为历史 evaluator 口径，不猜测新分数。

`site/results.json` 是公开结果的唯一数据源。修改后运行 `python3 scripts/sync_results.py` 刷新中英文 README 表格；`python3 scripts/verify_repository.py` 会检查公开页面与文档是否保持一致。

## DCI case

BrowseComp-Plus / DCI 的 canonical task 已包含在仓库中，但大 corpus 不上传 Git。完整运行前，按 [`cases/dci_browsecomp_architecture_firm_hard/README.md`](cases/dci_browsecomp_architecture_firm_hard/README.md) 从 Hugging Face 官方数据集一键 materialize payload。

## 快速开始

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
  --workspace /tmp/data-analysis-bench/prepbench
```

让自己的 agent 只在该 workspace 中完成 `task.md`，然后从仓库根目录评分：

```bash
python scripts/score_case.py \
  --case-id prepbench_loyalty_tier_normalization_hard \
  --workspace /tmp/data-analysis-bench/prepbench
```

评分报告默认写入 workspace 同级的 `score.json`。DV-World 和 BankerToolBench 的 official PASS 还要求视觉 judge；确定性评分通过后，设置 `BENCH_VISION_JUDGE_MODEL`、`BENCH_VISION_JUDGE_API_KEY` 和可选的 `BENCH_VISION_JUDGE_BASE_URL`，再增加 `--api-vision-judges`。版本化 prompt 位于对应的 `cases/<case_id>/truth/vision_judge_prompt.md`。详细评分约定见 [`EVALUATION.md`](EVALUATION.md)。

发布或修改 case 后运行完整性检查：

```bash
python scripts/verify_repository.py
```

## 数据和 Git LFS

LongDA 的大 CSV 和 Spider2-Lite 的 SQLite 文件由 Git LFS 管理。clone 后如未自动下载，可执行：

```bash
git lfs pull
```

第三方数据仍受各自上游许可证和访问条款约束，详见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

## 许可证

仓库代码使用 [MIT License](LICENSE)。Benchmark 数据和任务仍保留各自上游条款。
