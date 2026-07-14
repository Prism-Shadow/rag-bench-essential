# Potassium Repletion Orders in a Virtual EHR

This case is adapted from MedAgentBench task family 9. The task is an EHR
workflow, not a static question-answer lookup: for each patient, inspect the
most recent potassium result and, when clinically indicated by the provided
rule, prepare the paired medication and follow-up lab orders.

## Data

Read `data/README.md`, then inspect:

- `data/task9_subset.json` for the assigned patient tasks;
- `data/funcs_v1.json` for the available FHIR function schemas.

If a FHIR server is available, use the API base described in `env.md`.

## Task

For each assigned patient:

1. Find the patient by MRN if needed.
2. Query the most recent potassium Observation using code `K`.
3. Decide whether the potassium level is low against the goal/threshold of
   3.5 mEq/L or mmol/L.
4. If low, prepare an oral replacement potassium `MedicationRequest` using NDC
   `40032-917-01`. Dose rule: for every 0.1 mEq/L (or mmol/L) below 3.5, order
   10 mEq potassium oral repletion.
5. If low, also pair the medication order with a serum potassium lab
   `ServiceRequest` using LOINC `2823-3`, scheduled for the next day at 8am.
6. If not low, do not create replacement potassium or a paired lab order.

The task timestamp is `2023-11-13T10:15:00+00:00`, so the paired next-day lab
time is `2023-11-14T08:00:00+00:00`.

## Working Rules

- Work only from `task.md`, `env.md`, `env/`, and `data/`.
- You may use shell, Python, and `curl` from the workspace.
- Do not invent a potassium value. If no FHIR server is reachable, write a
  blocked status in `report.md` and still provide the action plan shape in
  `actions.json`.
- If you do issue live POST requests, record the exact request payloads in
  `actions.json`.

## Output Contract

Produce:

1. `actions.json`

   A JSON object with this shape. The values below are placeholders; fill them
   from the assigned task rows and the FHIR observations you query.

   ```json
   {
     "api_base": "<FHIR API base or offline-reference>",
     "patients": [
       {
         "mrn": "<assigned MRN>",
         "patient_reference": "Patient/<resolved patient id>",
         "potassium_query": {
           "method": "GET",
           "resource": "Observation",
           "params": {"patient": "Patient/<resolved patient id>", "code": "K"}
         },
         "most_recent_potassium": {
           "value": 0.0,
           "unit": "<mEq/L or mmol/L>",
           "effectiveDateTime": "<timestamp from selected Observation>"
         },
         "low": true,
         "replacement_order": {
           "resourceType": "MedicationRequest",
           "medicationCodeableConcept": {"coding": [{"code": "40032-917-01"}]},
           "dosageInstruction": [
             {
               "route": {"text": "oral"},
               "doseAndRate": [{"doseQuantity": {"value": 0.0, "unit": "mEq"}}]
             }
           ]
         },
         "followup_lab_order": {
           "resourceType": "ServiceRequest",
           "code": {"coding": [{"code": "2823-3"}]},
           "occurrenceDateTime": "2023-11-14T08:00:00+00:00"
         }
       }
     ]
   }
   ```

   Use `null` for `replacement_order` and `followup_lab_order` when the latest
   potassium value is not low.

2. `report.md`

   A short audit note describing which patients were processed, how the most
   recent potassium was selected, whether orders were posted or only prepared,
   and any environment limitation.
