# Rubric: Workspace-Bench Taobao Permissions

This case tests whether an agent can convert a heterogeneous workspace task into a grounded permission configuration without reading `truth/`.

| Step | What to inspect in trace | Expected behavior | Failure signature |
| --- | --- | --- | --- |
| Source discovery | Opens `data/README.md`, role definition, permission template, history log, and at least one activity spreadsheet/PPT/XLS source. | Treats the task as a cross-file workspace problem. | Uses only `task.md` and fabricates a generic RBAC table. |
| Default policy | Reads `系统权限模板.json`. | Sets `default_deny=true` and treats absent permissions as false. | Grants broad read/write because a role name sounds related. |
| Role semantics | Reads `角色定义.txt`. | Maps admin/operation/designer/service/stock to the five Chinese roles and their forbidden permissions. | Confuses service with operation, or stock with data analyst. |
| Historical checks | Reads `历史操作记录.json`. | Uses success/deny operations to validate activity apply, price view, inventory check and log query. | Gives service price visibility or stock activity apply despite deny records. |
| Permission matrix | Produces `淘宝活动/权限配置表.csv` with required columns and 5 x 9 role-module coverage. | Critical cells match expected read/write/download booleans. | Missing rows, Chinese-only non-standard module labels, or wrong booleans. |
| JSON rules | Produces `淘宝活动/权限校验规则.json`. | Defines `default_deny`, `roles`, `permissions`, and exact `sensitive_operations`. | `data_export` includes operation, or `activity_apply` includes stock/service. |
| Markdown explanation | Produces `淘宝活动/权限配置说明书.md`. | Explains role definitions, sensitive operations, price invisibility for service/stock, and default-deny principle. | Final files are present but audit note lacks source-grounded rationale. |

Hard gates:

- D1: `权限配置表.csv` has the required schema and critical permissions.
- D2: `权限校验规则.json` has exact `sensitive_operations` and `default_deny=true`.
- D3: `权限配置说明书.md` is non-trivial and mentions the load-bearing price-visibility rule.
- D4: all three required files exist under `淘宝活动/`.
