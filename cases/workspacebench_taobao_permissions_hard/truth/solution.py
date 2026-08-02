#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROLES = {
    "admin": "管理员",
    "operation": "运营",
    "designer": "美工",
    "service": "客服",
    "stock": "仓储",
}

PERMISSIONS = {
    "admin": {
        "activity_apply": (True, True, False, "角色定义: 管理层可活动审核; 模板默认禁止下显式授权"),
        "item_upshelf": (True, True, False, "管理员具备全量查看和管理权限"),
        "price_update": (True, True, False, "角色定义: 管理层可价格修改"),
        "material_edit": (True, True, False, "管理员具备全量查看和管理权限"),
        "inventory_data_view": (True, False, False, "管理员全量查看"),
        "order_data_view": (True, False, False, "管理员全量查看"),
        "data_export": (True, True, True, "角色定义: 管理层可数据导出"),
        "log_view": (True, False, False, "历史操作: admin log_query success"),
        "user_manager": (True, True, False, "角色定义: 管理层可用户管理"),
    },
    "operation": {
        "activity_apply": (True, True, False, "角色定义: 运营敏感权限含活动报名; 历史 activity_apply success"),
        "item_upshelf": (True, True, False, "角色定义: 运营敏感权限含商品上下架"),
        "price_update": (True, True, False, "角色定义: 运营敏感权限含价格设置; 历史 price_update success"),
        "material_edit": (True, False, False, "运营可查看活动素材, 但素材编辑归美工"),
        "inventory_data_view": (True, False, False, "运营需要查看库存支撑活动报名"),
        "order_data_view": (True, False, False, "角色定义: 运营基础权限含订单查看"),
        "data_export": (False, False, False, "模板敏感模块; 非管理员不授权导出"),
        "log_view": (False, False, False, "角色定义: 运营禁止日志查看"),
        "user_manager": (False, False, False, "角色定义: 运营禁止用户管理"),
    },
    "designer": {
        "activity_apply": (False, False, False, "角色定义: 美工禁止活动报名"),
        "item_upshelf": (False, False, False, "无商品上下架职责"),
        "price_update": (False, False, False, "角色定义: 美工禁止价格修改"),
        "material_edit": (True, True, False, "角色定义: 美工可图片上传、页面装修、素材编辑; 历史 material_upload success"),
        "inventory_data_view": (False, False, False, "无库存查看职责"),
        "order_data_view": (False, False, False, "无订单查看职责"),
        "data_export": (False, False, False, "非管理员不授权数据导出"),
        "log_view": (False, False, False, "无日志查看职责"),
        "user_manager": (False, False, False, "无用户管理职责"),
    },
    "service": {
        "activity_apply": (True, False, False, "角色定义: 客服可活动查看但禁止任何修改"),
        "item_upshelf": (False, False, False, "角色定义: 客服禁止任何修改"),
        "price_update": (False, False, False, "角色定义: 客服禁止价格查看; 历史 price_try_view deny"),
        "material_edit": (False, False, False, "角色定义: 客服禁止任何修改"),
        "inventory_data_view": (False, False, False, "无库存查看职责"),
        "order_data_view": (True, False, False, "角色定义: 客服基础权限含订单查看"),
        "data_export": (False, False, False, "角色定义: 客服禁止数据导出"),
        "log_view": (False, False, False, "无日志查看职责"),
        "user_manager": (False, False, False, "无用户管理职责"),
    },
    "stock": {
        "activity_apply": (False, False, False, "角色定义: 仓储禁止活动配置; 历史 activity_apply_try deny"),
        "item_upshelf": (False, False, False, "无商品上下架职责"),
        "price_update": (False, False, False, "角色定义: 仓储禁止价格查看"),
        "material_edit": (False, False, False, "无素材职责"),
        "inventory_data_view": (True, False, False, "角色定义: 仓储基础权限含库存查看; 历史 inventory_check success"),
        "order_data_view": (False, False, False, "无订单查看职责"),
        "data_export": (False, False, False, "角色定义: 仓储禁止数据导出"),
        "log_view": (False, False, False, "无日志查看职责"),
        "user_manager": (False, False, False, "无用户管理职责"),
    },
}

SENSITIVE = {
    "activity_apply": ["admin", "operation"],
    "item_upshelf": ["admin", "operation"],
    "price_update": ["admin", "operation"],
    "material_edit": ["admin", "designer"],
    "inventory_data_view": ["admin", "operation", "stock"],
    "order_data_view": ["admin", "operation", "service"],
    "data_export": ["admin"],
    "log_view": ["admin"],
    "user_manager": ["admin"],
}


def write_outputs() -> None:
    out = Path("淘宝活动")
    out.mkdir(exist_ok=True)

    with (out / "权限配置表.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["role", "module", "read", "write", "download", "basis"])
        writer.writeheader()
        for role, modules in PERMISSIONS.items():
            for module, (read, write, download, basis) in modules.items():
                writer.writerow({
                    "role": role,
                    "module": module,
                    "read": str(read).lower(),
                    "write": str(write).lower(),
                    "download": str(download).lower(),
                    "basis": basis,
                })

    permissions_json = {
        role: {
            module: {"read": read, "write": write, "download": download}
            for module, (read, write, download, _basis) in modules.items()
        }
        for role, modules in PERMISSIONS.items()
    }
    rules = {
        "default_deny": True,
        "roles": ROLES,
        "permissions": permissions_json,
        "sensitive_operations": SENSITIVE,
    }
    (out / "权限校验规则.json").write_text(
        json.dumps(rules, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# 电商活动系统权限配置说明书",
        "",
        "## 原则",
        "",
        "系统权限模板给出的默认权限是 read/write/download 全部为 false，因此本配置采用默认禁止原则；只有角色定义、历史操作记录或活动管理职责明确支持的权限才配置为 true。",
        "",
        "## 角色定义",
    ]
    for role, label in ROLES.items():
        lines.append(f"- `{role}`（{label}）")
    lines += [
        "",
        "## 敏感操作",
        "",
        "- `activity_apply` 只允许 admin 和 operation 写入；仓储的 activity_apply_try 在历史记录中被拒绝。",
        "- `price_update` 只允许 admin 和 operation；客服 price_try_view 被拒绝，仓储角色定义也禁止价格查看，因此客服和仓储对价格数据不可见。",
        "- `material_edit` 只允许 admin 和 designer 写入；美工角色定义包含图片上传、页面装修、素材编辑。",
        "- `data_export` 只允许 admin；其他角色不授予下载或导出。",
        "",
        "## 权限矩阵",
        "",
        "| role | module | read | write | download |",
        "| --- | --- | --- | --- | --- |",
    ]
    for role, modules in PERMISSIONS.items():
        for module, (read, write, download, _basis) in modules.items():
            lines.append(f"| {role} | {module} | {str(read).lower()} | {str(write).lower()} | {str(download).lower()} |")
    lines += [
        "",
        "## 价格数据说明",
        "",
        "客服的基础职责是订单查看、活动查看和售后处理，禁止任何修改、数据导出和价格查看；历史操作记录中客服尝试查看商品成本价被 deny。仓储职责是库存查看、发货确认和库存盘点，禁止价格查看、活动配置和数据导出。因此客服和仓储不能查看价格数据。",
    ]
    (out / "权限配置说明书.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write_outputs()
