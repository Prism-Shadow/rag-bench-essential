# Evaluation packages

每个 `cases/<case_id>/truth/` 通常包含：

- `rubric.yaml`：机器可读的评分点、权重、hard gate 和 failure layer；
- `RUBRIC.md`：面向人的简洁评分说明；
- `expected.json`：gold answer 和允许误差；
- `validate.py`：只读取最终交付物的确定性 validator；
- `solution.py`：用于审计 gold/validator 的 reference solution；
- 可选的 `vision_judge.yaml` 与 `vision_judge_prompt.md`；
- 个别 case 所需的 expected variants 或上游元数据。

这些文件不得出现在被测 agent 的 workspace 中。标准流程是：

1. 从 `cases/<case_id>/` 创建隔离 workspace；
2. 在 workspace 内运行 agent；
3. agent 结束后，从 workspace 外调用 `scripts/score_case.py`；
4. 保存最终 workspace、agent trace 和生成的 `score.json`。

Rubric 只评价任务要求的最终产物。trace 用于诊断，不作为 official PASS 的评分输入。
