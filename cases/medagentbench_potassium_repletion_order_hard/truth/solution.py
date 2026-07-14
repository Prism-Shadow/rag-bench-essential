#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def expected() -> dict:
    return json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))


def expected_dose(value: float, goal: float) -> float:
    import math

    if value >= goal:
        return 0.0
    return float(math.ceil(((goal - value) * 10) - 1e-9) * 10)


def medication_order(patient_ref: str, value: float, spec: dict) -> dict | None:
    dose = expected_dose(value, float(spec["goal"]))
    if dose <= 0:
        return None
    return {
        "resourceType": "MedicationRequest",
        "medicationCodeableConcept": {
            "coding": [{"system": "http://hl7.org/fhir/sid/ndc", "code": spec["replacement_ndc"]}],
            "text": "potassium oral repletion",
        },
        "authoredOn": "2023-11-13T10:15:00+00:00",
        "dosageInstruction": [
            {
                "route": {"text": spec["replacement_route"]},
                "doseAndRate": [{"doseQuantity": {"value": dose, "unit": spec["dose_unit"]}}],
            }
        ],
        "status": "active",
        "intent": "order",
        "subject": {"reference": patient_ref},
    }


def lab_order(patient_ref: str, spec: dict, needed: bool) -> dict | None:
    if not needed:
        return None
    return {
        "resourceType": "ServiceRequest",
        "code": {"coding": [{"system": "http://loinc.org", "code": spec["followup_loinc"]}]},
        "authoredOn": "2023-11-13T10:15:00+00:00",
        "status": "active",
        "intent": "order",
        "priority": "stat",
        "subject": {"reference": patient_ref},
        "occurrenceDateTime": spec["followup_time"],
    }


def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def resolve_patient(api_base: str, mrn: str) -> str:
    query = urllib.parse.urlencode({"identifier": mrn, "_format": "json"})
    url = urllib.parse.urljoin(api_base.rstrip("/") + "/", "Patient") + "?" + query
    bundle = fetch_json(url)
    patient_ids = [
        entry.get("resource", {}).get("id")
        for entry in bundle.get("entry", [])
        if entry.get("resource", {}).get("resourceType") == "Patient"
        and entry.get("resource", {}).get("id")
    ]
    if len(patient_ids) != 1:
        raise RuntimeError(
            f"expected exactly one Patient for MRN {mrn}, found {len(patient_ids)}"
        )
    return f"Patient/{patient_ids[0]}"


def latest_live_potassium(api_base: str, patient_ref: str) -> tuple[float, str] | None:
    query = urllib.parse.urlencode({"patient": patient_ref, "code": "K", "_format": "json"})
    url = urllib.parse.urljoin(api_base.rstrip("/") + "/", "Observation") + "?" + query
    bundle = fetch_json(url)
    latest = None
    for entry in bundle.get("entry", []):
        obs = entry.get("resource", {})
        stamp = obs.get("effectiveDateTime") or obs.get("issued")
        try:
            dt = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
            value = float(obs.get("valueQuantity", {}).get("value"))
        except Exception:
            continue
        if latest is None or dt > latest[0]:
            latest = (dt, value, stamp)
    if latest is None:
        return None
    return latest[1], latest[2]


def main() -> int:
    spec = expected()
    api_base = os.environ.get("FHIR_API_BASE")
    if not api_base:
        raise SystemExit("FHIR_API_BASE is required for the reference solution")
    patients = []
    for mrn in spec["patients"]:
        patient_ref = resolve_patient(api_base, mrn)
        live = latest_live_potassium(api_base, patient_ref)
        if live is None:
            raise RuntimeError(f"no potassium Observation found for {mrn}")
        value, stamp = live
        low = value < float(spec["goal"])
        patients.append({
            "mrn": mrn,
            "patient_reference": patient_ref,
            "potassium_query": {
                "method": "GET",
                "resource": "Observation",
                "params": {"patient": patient_ref, "code": spec["potassium_code"]},
            },
            "most_recent_potassium": {
                "value": value,
                "unit": "mEq/L",
                "effectiveDateTime": stamp,
            },
            "low": low,
            "replacement_order": medication_order(patient_ref, value, spec),
            "followup_lab_order": lab_order(patient_ref, spec, low),
        })

    Path("actions.json").write_text(json.dumps({"api_base": api_base, "patients": patients}, indent=2) + "\n", encoding="utf-8")
    Path("report.md").write_text(
        "# Potassium Repletion Audit\n\n"
        "Mode: live FHIR.\n\n"
        "Processed three MedAgentBench task9 patients. For each patient the action artifact records the Observation query for code K, the selected most recent potassium value, the low/not-low decision against 3.5, and the paired MedicationRequest and ServiceRequest payloads when replacement is indicated.\n",
        encoding="utf-8",
    )
    print("wrote actions.json and report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
