# PG dsv4pro v1.14 selected 15-case result

This package contains one selected trace, one external-validator log, and one
artifact manifest for each of the 15 retained cases.

## Result

- Prompt: `agent-configs/rag-agent/AGENTS.md`
- Full prompt SHA-256: `4e700e4c3ef8363dd7bac259f04a626cf45539af48881621f7ab984d32d56f83`
- Trace-embedded AGENTS body SHA-256: `8271c0128f91e74bd6ac20c24b065001e6743a9bd8d70c87318a06a8ff990b56`
- Coverage: 15/15
- Selected PASS: 10/15
- CC comparison: 10/15, with the same PASS set

PASS cases:

1. `spider2lite_f1_overtake_audit_hard`
2. `docfinqa_oilgas_canada_pdf_hard`
3. `longda_nscg_telework_hard`
4. `multihiertt_global_products_atoi_share_hard`
5. `bankertoolbench_cake_lbo_sensitivity_hard`
6. `dabstep_real_fees_1681`
7. `prepbench_loyalty_tier_normalization_hard`
8. `spreadsheetbench_working_paper_transpose_hard`
9. `harveylab_reps_diligence_discrepancy_hard`
10. `medagentbench_potassium_repletion_order_hard`

Shared PG/CC FAIL cases:

1. `dci_browsecomp_architecture_firm_hard`
2. `docvqa_contract_effective_date_ocr_hard`
3. `workspacebench_taobao_permissions_hard`
4. `dvworld_dvevol_crime_association_network_hard`
5. `finlongdocqa_interest_expense_sensitivity_screen_hard`

## Interpretation boundary

This is a selected best-of-retries result, not one contemporaneous single-shot
15-case batch. Before targeted retries, the assembled exact-v1.14 coverage had
7/15 PASS. The selected set reaches 10/15 after normal targeted retries recovered
Spider2-Lite, MultiHiertt, and MedAgentBench. Abnormal connection-error and
terminated attempts are not substituted into this package.

Spider2-Lite passed on its third normal v1.14 attempt. MultiHiertt passed on the
next normal run after an abnormal terminated batch. MedAgentBench passes the
repository's canonical artifact/action contract; its trace also shows live FHIR
reads and the two intended live order POSTs for only the low-potassium patient.
The optional live validator currently reads only the first FHIR result page, so
its false latest-value mismatch is not used as the selected PASS basis.

`manifest.tsv` is the machine-readable index. `SHA256SUMS` binds all packaged
traces, validation logs, and artifact manifests.
