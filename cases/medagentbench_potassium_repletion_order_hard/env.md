# Environment

This case can be run in two modes.

## Live MedAgentBench mode

Use the MedAgentBench FHIR server:

```text
FHIR_API_BASE=http://localhost:8080/fhir/
```

If the server is not already running, `env/setup.sh` can start it using the
public Docker image described by MedAgentBench. The Docker daemon must be
available locally.

## Offline artifact mode

If the FHIR server is unavailable, the agent may still produce `actions.json`
with the intended query/order payload shape and a `report.md` explaining that
live EHR side effects could not be completed. This mode checks artifact shape
only and does not receive a passing validator result. A complete run must set a
reachable `FHIR_API_BASE` so the latest observations can be re-queried and the
order decision can be grounded in live data.
