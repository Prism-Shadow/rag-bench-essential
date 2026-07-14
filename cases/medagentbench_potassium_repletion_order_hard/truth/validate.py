#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def load_expected() -> dict:
    return json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def normalize_reference(value: str | None) -> str:
    raw = str(value or "").strip()
    return raw if raw.startswith("Patient/") else f"Patient/{raw}" if raw else ""


def find_code(obj, code: str) -> bool:
    if isinstance(obj, dict):
        return any(find_code(v, code) for v in obj.values())
    if isinstance(obj, list):
        return any(find_code(v, code) for v in obj)
    return str(obj).strip().lower() == code.lower()


def find_number_with_unit(obj, unit: str) -> float | None:
    if isinstance(obj, dict):
        unit_text = str(obj.get("unit", "")).lower()
        if unit.lower() in unit_text and "value" in obj:
            try:
                return float(obj["value"])
            except Exception:
                return None
        for value in obj.values():
            found = find_number_with_unit(value, unit)
            if found is not None:
                return found
    if isinstance(obj, list):
        for value in obj:
            found = find_number_with_unit(value, unit)
            if found is not None:
                return found
    return None


def expected_dose(value: float, goal: float) -> float:
    if value >= goal:
        return 0.0
    tenths = math.ceil(((goal - value) * 10) - 1e-9)
    return float(tenths * 10)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def patient_rows(actions: dict) -> dict[str, dict]:
    rows = actions.get("patients")
    if isinstance(rows, list):
        return {str(row.get("mrn")): row for row in rows if isinstance(row, dict)}
    if isinstance(rows, dict):
        return {str(k): v for k, v in rows.items() if isinstance(v, dict)}
    return {}


def score_patient(mrn: str, row: dict, expected: dict) -> bool:
    ok = True
    print(f"  Patient {mrn}")
    query_blob = json.dumps(row.get("potassium_query", {}), ensure_ascii=False).lower()
    query_ok = "observation" in query_blob and expected["potassium_code"].lower() in query_blob
    print(f"    [{'OK ' if query_ok else 'MISS'}] potassium Observation query recorded")
    ok = ok and query_ok

    obs = row.get("most_recent_potassium", {})
    if not isinstance(obs, dict):
        obs = {}
    try:
        value = float(obs.get("value"))
    except Exception:
        value = None
    date_ok = parse_dt(obs.get("effectiveDateTime") or obs.get("issued")) is not None
    value_ok = value is not None and -1.0 <= value <= 8.0
    print(f"    [{'OK ' if value_ok else 'MISS'}] numeric potassium value: {value}")
    print(f"    [{'OK ' if date_ok else 'MISS'}] observation timestamp present")
    ok = ok and value_ok and date_ok
    if value is None:
        return False

    low_expected = value < float(expected["goal"])
    low_got = row.get("low")
    low_ok = low_got is low_expected
    print(f"    [{'OK ' if low_ok else 'MISS'}] low flag expected={low_expected} got={low_got}")
    ok = ok and low_ok

    replacement = row.get("replacement_order")
    lab = row.get("followup_lab_order")
    if not low_expected:
        no_order_ok = replacement in (None, {}, False) and lab in (None, {}, False)
        print(f"    [{'OK ' if no_order_ok else 'MISS'}] no replacement/lab order when potassium is not low")
        return ok and no_order_ok

    repl_blob = json.dumps(replacement or {}, ensure_ascii=False).lower()
    lab_blob = json.dumps(lab or {}, ensure_ascii=False).lower()
    ndc_ok = expected["replacement_ndc"].lower() in repl_blob
    route_ok = expected["replacement_route"].lower() in repl_blob
    dose_value = find_number_with_unit(replacement, expected["dose_unit"])
    dose_ok = dose_value is not None and abs(dose_value - expected_dose(value, float(expected["goal"]))) <= 0.01
    loinc_ok = expected["followup_loinc"].lower() in lab_blob
    time_ok = expected["followup_time"].lower() in lab_blob
    print(f"    [{'OK ' if ndc_ok else 'MISS'}] replacement NDC {expected['replacement_ndc']}")
    print(f"    [{'OK ' if route_ok else 'MISS'}] oral route")
    print(f"    [{'OK ' if dose_ok else 'MISS'}] dose={dose_value}, expected={expected_dose(value, float(expected['goal']))} {expected['dose_unit']}")
    print(f"    [{'OK ' if loinc_ok else 'MISS'}] follow-up lab LOINC {expected['followup_loinc']}")
    print(f"    [{'OK ' if time_ok else 'MISS'}] follow-up lab next day 8am")
    return ok and ndc_ok and route_ok and dose_ok and loinc_ok and time_ok


def fetch_live_observations(api_base: str, patient_ref: str) -> list[dict]:
    query = urllib.parse.urlencode({"patient": patient_ref, "code": "K", "_format": "json"})
    url = urllib.parse.urljoin(api_base.rstrip("/") + "/", "Observation") + "?" + query
    with urllib.request.urlopen(url, timeout=5) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return [entry.get("resource", {}) for entry in payload.get("entry", [])]


def live_check(actions: dict, expected: dict) -> bool | None:
    api_base = os.environ.get("FHIR_API_BASE")
    if not api_base:
        print("== Live FHIR check ==")
        print("  [INFO] FHIR_API_BASE not set; artifact-only validation")
        return None
    rows = patient_rows(actions)
    all_ok = True
    print("== Live FHIR check ==")
    for mrn in expected["patients"]:
        row = rows.get(mrn, {})
        patient_ref = normalize_reference(row.get("patient_reference") or row.get("patient_id"))
        if not patient_ref:
            print(f"  [MISS] {mrn}: no patient_reference for live check")
            all_ok = False
            continue
        try:
            observations = fetch_live_observations(api_base, patient_ref)
        except Exception as exc:
            print(f"  [INFO] {mrn}: live check unavailable: {exc}")
            print("  [INFO] continuing with artifact-only validation")
            return None
        latest = None
        for obs in observations:
            dt = parse_dt(obs.get("effectiveDateTime") or obs.get("issued"))
            if dt is None:
                continue
            if latest is None or dt > latest[0]:
                latest = (dt, obs)
        if latest is None:
            print(f"  [MISS] {mrn}: no potassium Observation in live FHIR response")
            all_ok = False
            continue
        live_value = latest[1].get("valueQuantity", {}).get("value")
        got_obs = row.get("most_recent_potassium", {})
        if not isinstance(got_obs, dict):
            got_obs = {}
        got_value = got_obs.get("value")
        try:
            match = abs(float(live_value) - float(got_value)) <= 1e-6
        except Exception:
            match = False
        print(f"  [{'OK ' if match else 'MISS'}] {mrn}: live latest K={live_value}, actions.json={got_value}")
        all_ok = all_ok and match
    return all_ok


def main() -> int:
    expected = load_expected()
    missing = [path for path in expected["required_files"] if not Path(path).exists()]
    if missing:
        print("FAIL: required output files missing:")
        for path in missing:
            print(f"  - {path}")
        return 2

    actions = load_json(Path("actions.json"))
    if not isinstance(actions, dict):
        print("FAIL: actions.json is missing or not a JSON object")
        return 2

    print("== D1/D3 clinical action consistency ==")
    rows = patient_rows(actions)
    patients_ok = sorted(rows) == sorted(expected["patients"])
    print(f"  [{'OK ' if patients_ok else 'MISS'}] patients present expected={expected['patients']} got={sorted(rows)}")
    action_ok = patients_ok
    for mrn in expected["patients"]:
        action_ok = score_patient(mrn, rows.get(mrn, {}), expected) and action_ok

    print("== D4 delivery ==")
    report = Path("report.md")
    report_text = report.read_text(encoding="utf-8", errors="ignore") if report.exists() else ""
    report_ok = len(report_text.strip()) >= 200 and ("potassium" in report_text.lower() or "fhir" in report_text.lower())
    print(f"  [{'OK ' if report_ok else 'MISS'}] report.md non-trivial")

    live = live_check(actions, expected)

    if action_ok and report_ok and live is True:
        print("\nRESULT: PASS - artifact/action contract passed and live FHIR grounding was verified.")
        return 0
    if action_ok and report_ok and live is None:
        print("\nRESULT: FAIL - artifact/action contract passed, but live FHIR grounding was not verified.")
        return 1
    print("\nRESULT: FAIL - action contract, report, or live FHIR verification failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
