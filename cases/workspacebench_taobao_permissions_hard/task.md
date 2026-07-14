# 电商活动系统权限配置

根据淘宝电商活动规则文档、活动报名记录、历史操作日志与系统角色定义，推断并生成管理员 / 运营 / 美工 / 客服 / 仓储五种角色对活动配置、商品上下架、价格修改、素材编辑、数据查看等功能的权限范围。

本任务改造自 Workspace-Bench-Lite 的异构 workspace case。你需要在本地 workspace 内完成文件理解、跨源对齐和交付物生成。

## 数据

请先阅读 `data/README.md`，再检查 `data/` 下的原始文件。输入包含多种格式：

- `.xlsx` 活动规则、报名跟进和活动总结表格。
- `.xls` 历史活动小结。
- `.ppt` 活动方案。
- `.json` 历史操作记录和系统权限模板。
- `.txt` 角色定义。

## 任务

综合所有相关文件，推断五种角色的权限配置：

- `admin`: 管理员
- `operation`: 运营
- `designer`: 美工
- `service`: 客服
- `stock`: 仓储

至少覆盖以下功能模块：

- `activity_apply`: 活动报名 / 活动配置
- `item_upshelf`: 商品上下架
- `price_update`: 价格修改
- `material_edit`: 素材编辑
- `inventory_data_view`: 库存数据查看
- `order_data_view`: 订单 / 活动数据查看
- `data_export`: 数据导出
- `log_view`: 操作日志查看
- `user_manager`: 用户管理

权限默认遵循 deny-by-default：没有证据支持的读、写、下载权限都应视为 `false`。

## 输出契约

请在 workspace 相对路径 `淘宝活动/` 下生成 3 个文件：

1. `淘宝活动/权限配置表.csv`
   - UTF-8 CSV。
   - 表头必须为：`role,module,read,write,download,basis`
   - `role` 和 `module` 使用上面列出的英文标识。
   - `read/write/download` 使用小写 `true` 或 `false`。
   - `basis` 简要说明该权限来自哪些文件或规则。

2. `淘宝活动/权限配置说明书.md`
   - 说明五种角色定义、职责范围、权限矩阵、敏感操作说明和默认禁止原则。
   - 必须解释客服和仓储为什么不能查看价格数据。

3. `淘宝活动/权限校验规则.json`
   - 必须是可解析 JSON。
   - 至少包含：
     - `default_deny: true`
     - `roles`
     - `permissions`
     - `sensitive_operations`
   - `sensitive_operations.activity_apply` 只能包含 `admin` 和 `operation`。
   - `sensitive_operations.data_export` 只能包含 `admin`。

## 工作规则

- 只使用当前 workspace 中的 `task.md`、`env.md` 和 `data/`。
- 可以在 workspace 内写临时脚本，但最终必须按上面的路径产出 3 个交付文件。
