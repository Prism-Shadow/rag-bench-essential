# Data

This directory contains the agent-visible portion of a MedAgentBench task
family 9 adaptation.

## Files

| File | Role |
| --- | --- |
| `task9_subset.json` | Three assigned potassium repletion tasks. |
| `funcs_v1.json` | FHIR function/API schema published with MedAgentBench. |

## Lineage

The task wording and FHIR function schema come from MedAgentBench, a 2025
virtual EHR benchmark. The original benchmark evaluates agents through a live
FHIR server and a hidden reference solution. This case keeps the live-service
shape while adding an artifact contract suitable for this bench lab.

## Caution

The public task file does not contain patient potassium values. Those values
must be obtained from the FHIR server when it is available. The output should
therefore record both the query used and the order payloads prepared or posted.
