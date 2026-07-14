# Rubric

This case grades a legal diligence memo against the Harvey LAB source rubric.
The agent-visible task preserves the original deliverable shape:
`reps-vs-diligence-memo.docx`.

## Scoring Dimensions

| Dimension | Gate | Failure signature |
| --- | --- | --- |
| D1 discrepancy coverage | At least 10 of 14 planted material discrepancies are identified with their load-bearing facts. | Memo summarizes the transaction but misses concrete conflicts or omissions. |
| D2 source and section binding | Memo names enough SPA sections/schedules and diligence sources to bind findings to evidence. | Findings are plausible but float without the representation or diligence source. |
| D3 memo controls | Memo includes severity ratings and concrete recommended actions. | Memo is issue spotting only, with no deal-team action path. |
| D4 delivery | Required `.docx` exists and contains non-trivial readable text. | Agent writes no file, writes only markdown, or writes an unreadable docx. |

## Key Trace Checks

- Did the agent inspect both legal documents and diligence support, rather than
  only the SPA or only the diligence summary?
- Did it parse the Excel workpapers for contract and EBITDA issues?
- Did it connect issue facts to SPA sections or disclosure schedules?
- Did it preserve the original output contract, or stop after drafting notes in
  a scratch file?

## Stable Decoys

- SPA-only summary: mentions representations but misses diligence conflicts.
- Diligence-only issue list: identifies risks without tying them to SPA reps or
  schedules.
- Generic deal-risk memo: uses legal boilerplate without the planted facts.
