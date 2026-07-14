# Run Protocol

以下流程适用于本仓库中可直接运行的 case。DCI/BrowseComp-Plus case 需要先按其目录内说明，在本地补齐受限 payload；受限内容不得提交到仓库。

## 1. 建立隔离 workspace

不要在 `cases/` 目录中直接运行 Agent。为每次运行建立独立 workspace，并且只复制 Agent 可见材料：

```bash
CASE=spider2lite_f1_overtake_audit_hard
REPO_ROOT="$(pwd)"
WORKSPACE="${TMPDIR:-/tmp}/rag-bench/${CASE}/workspace"

rm -rf "$WORKSPACE"
mkdir -p "$WORKSPACE"
cp "$REPO_ROOT/cases/$CASE/task.md" "$WORKSPACE/"
cp -R "$REPO_ROOT/cases/$CASE/data" "$WORKSPACE/"
test ! -f "$REPO_ROOT/cases/$CASE/env.md" || cp "$REPO_ROOT/cases/$CASE/env.md" "$WORKSPACE/"
```

workspace 只能包含 `task.md`、`data/` 和可选 `env.md`。绝不能复制 `truth/`。

如果 case 提供 `env/setup.sh`，先在仓库侧执行并按其输出设置环境变量；运行结束后执行对应的 `env/teardown.sh`。

## 2. 运行 Agent

将 Agent 的工作目录设为 `$WORKSPACE`。PG Agent 使用仓库中的专用配置：

```text
agent-configs/pg-dsv4pro/current/AGENTS.md
```

具体 Agent CLI 命令由运行环境决定。本仓库不固定本机路径，也不把某个 Agent 项目的源码目录写入协议。

## 3. 外部验证

Agent 结束后，从 workspace 内调用 case validator，并通过 `BENCH_TRUTH_DIR` 显式提供只对 validator 可见的 truth 路径：

```bash
(
  cd "$WORKSPACE"
  BENCH_TRUTH_DIR="$REPO_ROOT/cases/$CASE/truth" \
    python3 "$REPO_ROOT/cases/$CASE/truth/validate.py"
)
```

validator 的退出码是机器判定；标准输出用于检查各评分维度。运行产物、trace 和分析报告应在清理并确认不包含受限数据或凭据后再发布。

## 4. 环境清理

如果 case 提供 teardown：

```bash
test ! -x "$REPO_ROOT/cases/$CASE/env/teardown.sh" || \
  "$REPO_ROOT/cases/$CASE/env/teardown.sh"
```

MedAgentBench 需要 live FHIR 服务才能得到完整通过判定；离线 artifact 只能用于检查交付结构，不能替代 live grounding。
