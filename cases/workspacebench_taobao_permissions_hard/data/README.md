# Data README

## Lineage

This case is adapted from Workspace-Bench-Lite, a benchmark for workspace tasks
with large-scale heterogeneous file dependencies. The original task is a Backend
Developer workspace case about deriving an e-commerce campaign permission
configuration from mixed office and structured files.

## Files

| File | Type | Role in the task |
| --- | --- | --- |
| `11b16ba2e69b04ec__活动_淘内热门规则资料整理.xlsx` | Excel | Taobao internal campaign rule references and activity links. |
| `74e3fcaf324321bd__活动_淘宝活动跟进表.xlsx` | Excel | Campaign application follow-up records, including application method, product, price, activity price and review status. |
| `e5e3b2d3b0d40652__活动总结_淘宝站内站外活动要求总结.xlsx` | Excel | On-site and off-site activity requirement summary. |
| `ff96d788c746c3b4__活动_天天特价_淘金币活动小结.xls` | legacy Excel | Historical campaign notes in older Office format. |
| `c903c05cb499b95c__活动方案_淘抢购必抢方案.ppt` | legacy PowerPoint | Campaign plan material in older Office format. |
| `387ed9d805f6d4dd_历史操作记录.json` | JSON | Observed successful and denied operations by role. |
| `e4eb33b72b954d65_系统权限模板.json` | JSON | Default permission policy, sensitive modules and file-permission template. |
| `ecfd4ce97ab51c9e_角色定义.txt` | text | Role definitions, base permissions, sensitive permissions and forbidden permissions. |

## Caution

- The activity spreadsheets describe campaign rules and operational context; they are not a ready-made permission table.
- The load-bearing permission evidence is distributed across the role definition, permission template and historical operation log.
- The old `.ppt` and `.xls` files are intentionally preserved to keep the heterogeneous workspace shape. A robust agent should inspect what it can extract, then cross-check against the structured JSON/text sources instead of assuming one file is authoritative.
- Use deny-by-default for any permission not supported by the visible files.
