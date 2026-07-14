# Rubric

This case adapts MedAgentBench task family 9 into the bench lab's artifact
contract.

## Scoring Dimensions

| Dimension | Gate | Failure signature |
| --- | --- | --- |
| D1 patient/action coverage | `actions.json` contains all assigned MRNs and a potassium Observation query for each. | Agent skips a patient or gives a narrative answer without an action artifact. |
| D2 live evidence binding | When `FHIR_API_BASE` is reachable, the selected potassium value matches the latest live FHIR Observation. | Agent uses a stale, invented, or unbound potassium value. |
| D3 dosing/order semantics | Low flag, replacement NDC, oral dose, and paired next-day LOINC lab agree with the task rule. | Wrong dose, unconditional order, or missing paired lab. |
| D4 delivery | `actions.json` and a non-trivial `report.md` exist. | Agent completes reasoning but does not write required artifacts. |

Offline runs can receive D1/D3/D4 credit for producing a coherent action
artifact, but D2 is not established unless the live FHIR server is reachable.
Do not interpret an offline artifact pass as proof that the potassium values
were grounded in the EHR.

## Trace Checks

- Did the agent query `Observation` with code `K` for each MRN or patient
  reference?
- Did it sort or otherwise choose the most recent potassium result?
- Did it compute dose from the distance below 3.5 instead of using a fixed dose?
- Did it pair replacement with a serum potassium `ServiceRequest` at
  `2023-11-14T08:00:00+00:00`?
- Did it clearly distinguish prepared payloads from POSTed live orders?
