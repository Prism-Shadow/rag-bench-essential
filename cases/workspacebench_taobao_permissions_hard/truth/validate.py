#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path


ROLE_ALIASES = {
    "管理员": "admin",
    "admin": "admin",
    "运营": "operation",
    "operation": "operation",
    "美工": "designer",
    "设计": "designer",
    "designer": "designer",
    "客服": "service",
    "service": "service",
    "仓储": "stock",
    "库存": "stock",
    "stock": "stock",
}

MODULE_ALIASES = {
    "activity_apply": "activity_apply",
    "活动报名": "activity_apply",
    "活动配置": "activity_apply",
    "item_upshelf": "item_upshelf",
    "商品上下架": "item_upshelf",
    "上下架": "item_upshelf",
    "price_update": "price_update",
    "价格修改": "price_update",
    "价格": "price_update",
    "material_edit": "material_edit",
    "素材编辑": "material_edit",
    "素材": "material_edit",
    "inventory_data_view": "inventory_data_view",
    "库存数据查看": "inventory_data_view",
    "库存": "inventory_data_view",
    "order_data_view": "order_data_view",
    "订单数据查看": "order_data_view",
    "订单": "order_data_view",
    "活动数据查看": "order_data_view",
    "data_export": "data_export",
    "数据导出": "data_export",
    "导出": "data_export",
    "log_view": "log_view",
    "日志查看": "log_view",
    "操作日志": "log_view",
    "user_manager": "user_manager",
    "用户管理": "user_manager",
}


def truth_dir() -> Path:
    env = os.environ.get("BENCH_TRUTH_DIR")
    return Path(env) if env else Path(__file__).resolve().parent


def load_expected() -> dict:
    return json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def normalize_role(value: str) -> str:
    raw = str(value or "").strip()
    low = raw.lower()
    if low in ROLE_ALIASES:
        return ROLE_ALIASES[low]
    for token, role in ROLE_ALIASES.items():
        if token and token in raw:
            return role
    return low


def normalize_module(value: str) -> str:
    raw = str(value or "").strip()
    low = raw.lower()
    if low in MODULE_ALIASES:
        return MODULE_ALIASES[low]
    for token, module in MODULE_ALIASES.items():
        if token and token in raw:
            return module
    return low


def parse_bool(value) -> bool | None:
    if isinstance(value, bool):
        return value
    s = str(value or "").strip().lower()
    if s in {"true", "1", "yes", "y", "是", "可", "允许", "read", "write"}:
        return True
    if s in {"false", "0", "no", "n", "否", "不可", "禁止", "deny", ""}:
        return False
    return None


def missing_files(expected: dict) -> list[str]:
    return [p for p in expected["required_files"] if not Path(p).exists()]


def score_csv(expected: dict) -> bool:
    path = Path("淘宝活动/权限配置表.csv")
    try:
        rows = list(csv.DictReader(path.open("r", encoding="utf-8-sig", newline="")))
    except Exception as exc:
        print(f"  [MISS] CSV unreadable: {exc}")
        return False

    required_cols = {"role", "module", "read", "write", "download", "basis"}
    cols = set(rows[0].keys()) if rows else set()
    cols_ok = required_cols.issubset(cols)
    print(f"  [{'OK ' if cols_ok else 'MISS'}] CSV columns include {sorted(required_cols)}")
    if not cols_ok:
        return False

    matrix: dict[tuple[str, str], dict[str, bool]] = {}
    for row in rows:
        role = normalize_role(row.get("role", ""))
        module = normalize_module(row.get("module", ""))
        if not role or not module:
            continue
        matrix[(role, module)] = {
            "read": parse_bool(row.get("read")),
            "write": parse_bool(row.get("write")),
            "download": parse_bool(row.get("download")),
        }

    ok = True
    total = matched = 0
    for role, modules in expected["permissions"].items():
        for module, exp_perm in modules.items():
            total += 1
            got = matrix.get((role, module))
            if got is None:
                print(f"  [MISS] CSV missing row: {role}.{module}")
                ok = False
                continue
            checks = ["read", "write"]
            if module == "data_export":
                checks.append("download")
            row_ok = all(got.get(key) is exp_perm.get(key) for key in checks)
            matched += bool(row_ok)
            if not row_ok:
                print(f"  [MISS] CSV {role}.{module}: expected={exp_perm} got={got}")
                ok = False
    print(f"  CSV permission cells matched {matched}/{total}")
    return ok


def normalize_role_list(values) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted({normalize_role(v) for v in values})


def score_json_rules(expected: dict) -> bool:
    path = Path("淘宝活动/权限校验规则.json")
    rules = load_json(path)
    if not isinstance(rules, dict):
        print("  [MISS] JSON rules missing or unreadable")
        return False

    ok = True
    default_deny = rules.get("default_deny")
    default_ok = default_deny is True
    print(f"  [{'OK ' if default_ok else 'MISS'}] default_deny=true")
    ok = ok and default_ok

    sensitive = rules.get("sensitive_operations", {})
    if not isinstance(sensitive, dict):
        print("  [MISS] sensitive_operations must be an object")
        return False

    # Public task.md only hard-specifies exact sensitive role lists for these
    # two modules. Other sensitive-operation entries are useful audit detail,
    # but should not be a hard validator gate unless task.md asks for them.
    required_sensitive_modules = ("activity_apply", "data_export")
    for module in required_sensitive_modules:
        exp_roles = expected["sensitive_operations"][module]
        got_roles = normalize_role_list(sensitive.get(module))
        exp_norm = sorted(exp_roles)
        match = got_roles == exp_norm
        print(f"  [{'OK ' if match else 'MISS'}] sensitive_operations.{module}: expected={exp_norm} got={got_roles}")
        ok = ok and match
    return ok


def score_markdown(expected: dict) -> bool:
    path = Path("淘宝活动/权限配置说明书.md")
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        print("  [MISS] Markdown report missing or unreadable")
        return False
    nontrivial = len(text.strip()) >= 500
    tokens = expected.get("required_markdown_tokens", [])
    token_hits = [token for token in tokens if token in text]
    token_ok = len(token_hits) == len(tokens)
    price_deny_ok = ("客服" in text and "仓储" in text and "价格" in text and ("不可见" in text or "禁止" in text or "false" in text))
    print(f"  [{'OK ' if nontrivial else 'MISS'}] Markdown non-trivial")
    print(f"  [{'OK ' if token_ok else 'MISS'}] Markdown required tokens {len(token_hits)}/{len(tokens)}")
    print(f"  [{'OK ' if price_deny_ok else 'MISS'}] Markdown explains price invisibility for service/stock")
    return nontrivial and token_ok and price_deny_ok


def main() -> int:
    expected = load_expected()
    missing = missing_files(expected)
    if missing:
        print("FAIL: required output files missing:")
        for path in missing:
            print(f"  - {path}")
        return 2

    print("== D1 permission table ==")
    csv_ok = score_csv(expected)
    print("== D2 JSON rule binding ==")
    json_ok = score_json_rules(expected)
    print("== D3 Markdown audit note ==")
    md_ok = score_markdown(expected)
    print("== D4 delivery ==")
    delivery_ok = not missing
    print(f"  [{'OK ' if delivery_ok else 'MISS'}] all required files present")

    if csv_ok and json_ok and md_ok and delivery_ok:
        print("\nRESULT: PASS - permission matrix, rule JSON, and delivery all pass.")
        return 0
    print("\nRESULT: FAIL - see dimension diagnostics above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
