# Data Analysis Bench

Languages: [English](README.md) | [中文](README.zh.md) | [Results site](https://prism-shadow.github.io/rag-bench-essential/)

Data Analysis Bench is a reproducible suite of 15 difficult, production-shaped tasks for evaluating end-to-end data-analysis agents. It spans long documents, scanned pages, hierarchical tables, spreadsheets, SQLite databases, multi-source workflows, analytical reasoning, visualization, and delivery requirements.

The repository includes each public task payload together with the rubric, gold answer, validator, reference solution, and optional visual-judge prompt needed to reproduce official scoring. Other agents can be staged and evaluated using this repository alone.

Each `cases/<case_id>/` directory contains two kinds of material:

- agent-visible `task.md`, `data/`, and optional `env.md`;
- evaluator-only `truth/`, containing the rubric, gold data, validator, reference solution, and any visual-judge configuration.

Evaluator material is versioned for reproducibility, but it must never be copied into the tested agent's workspace. `scripts/stage_case.py` only stages `task.md`, `data/`, and `env.md`.

## Benchmark cases

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

Each setting retains one complete 15-case run. Accuracy is the number of official hard PASS results; time is averaged per case; token usage is the full-suite total. Cost is labeled **recorded cost** because Penguin settings could call `google/gemini-3.6-flash` for visual input and the OpenRouter proxy cost was not retained. Claude Code and Codex did not have that auxiliary vision tool.

<!-- RESULTS_TABLE_START -->
| Setting | Version and configuration | Accuracy | Avg. time / case (min) | Total tokens (M/run) | Recorded cost (USD/run) | Result basis |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Penguin w/ Manual Skill | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / manual Skill / Goal off | 11/15 (73.3%) | 6.52 | 12.38 | $0.1995 | Historical evaluator |
| Penguin w/ Manual Skill + Goal | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / manual Skill / Goal on | 11/15 (73.3%) | 5.84 | 17.65 | $0.2267 | Historical evaluator |
| Penguin w/ Auto-optimized Agent State | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / one-round auto-optimized Agent State / Goal off | 10/15 (66.7%) | 6.29 | 13.75 | $0.2158 | Historical evaluator |
| Claude Code | Claude Code CLI 2.1.191 / Claude Opus 4.8 / effort=max | 10/15 (66.7%) | 10.61 | 16.93 | $34.27 | Current evaluator |
| Codex | Codex CLI 0.146.0-alpha.9.2 / GPT-5.5 xhigh / no skill | 10/15 (66.7%) | 7.26 | 12.22 | $18.94 | Historical evaluator |
| Penguin w/o Skill | PenguinHarness v0.1.5 / DeepSeek V4 Flash xhigh / no skill / Goal off | 9/15 (60.0%) | 5.99 | 17.78 | $0.2231 | Historical evaluator |
| Penguin w/ Manual Skill | PenguinHarness v0.0.1 / DeepSeek V4 Flash xhigh / manual Skill / Goal off | 9/15 (60.0%) | 6.51 | 16.44 | $0.2250 | Historical evaluator |
| Penguin w/o Skill | PenguinHarness v0.0.1 / DeepSeek V4 Flash xhigh / no skill / Goal off | 8/15 (53.3%) | 9.10 | 18.51 | $0.2407 | Historical evaluator |
<!-- RESULTS_TABLE_END -->

Claude Code's 10/15 includes the BankerToolBench regrade after the 2026-08-10 evaluator fix. Its saved visual verdict remains valid because it is bound to the deliverable SHA. The other seven settings did not retain the required workspace artifact, so their published scores remain explicitly marked as historical rather than being guessed under the new evaluator.

`site/results.json` is the canonical published result source. After changing it, run `python3 scripts/sync_results.py` to refresh both README tables; `python3 scripts/verify_repository.py` checks that the public surfaces remain aligned.

## DCI case

The canonical BrowseComp-Plus / DCI task is included, but its large corpus is not committed to Git. Before a full run, materialize its payload from the official Hugging Face dataset as described in [`cases/dci_browsecomp_architecture_firm_hard/README.md`](cases/dci_browsecomp_architecture_firm_hard/README.md).

## Quick start

Install scoring dependencies and pull Git LFS data:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-eval.txt
git lfs pull
```

Stage an isolated workspace for one case:

```bash
python scripts/stage_case.py \
  --case-id prepbench_loyalty_tier_normalization_hard \
  --workspace /tmp/data-analysis-bench/prepbench
```

Run your agent only inside that workspace, then score the deliverable from the repository root:

```bash
python scripts/score_case.py \
  --case-id prepbench_loyalty_tier_normalization_hard \
  --workspace /tmp/data-analysis-bench/prepbench
```

The score report is written to `score.json` beside the workspace by default. Official PASS for DV-World and BankerToolBench also requires a visual judge. After deterministic scoring succeeds, set `BENCH_VISION_JUDGE_MODEL`, `BENCH_VISION_JUDGE_API_KEY`, and optionally `BENCH_VISION_JUDGE_BASE_URL`, then add `--api-vision-judges`. The versioned prompt is stored in the corresponding `cases/<case_id>/truth/vision_judge_prompt.md`. See [`EVALUATION.md`](EVALUATION.md) for the full scoring contract.

Run the repository integrity check after publishing or modifying a case:

```bash
python scripts/verify_repository.py
```

## Data and Git LFS

The LongDA CSV and Spider2-Lite SQLite database are managed with Git LFS. If they were not downloaded automatically after clone, run:

```bash
git lfs pull
```

Third-party data remains subject to its upstream license and access terms. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## License

Repository code is released under the [MIT License](LICENSE). Benchmark data and source tasks retain their respective upstream terms.
