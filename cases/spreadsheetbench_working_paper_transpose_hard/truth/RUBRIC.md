# Trace Audit Rubric

| Step | What to Check in Trace | Failure Signature |
| --- | --- | --- |
| 1. Workbook routing | Agent opens all three public `.xlsx` workbooks and identifies `destination`, `lap-1`, `lap-2`, `lap-9`. | Completes only one variant or ignores one source sheet. |
| 2. Layout recognition | Agent notices that `lap-*` sheets are repeated working-paper forms, not flat tables. | Uses a CSV/header style parser and loses coordinate layout. |
| 3. Highlight / coordinate binding | Agent binds the transposed values to the specified local coordinates in the exact task order: `C3, C4, C5, C7, C8, C11, C12, E9, E11, E12, C15, C21`. | Extracts only the first block, uses wrong offsets, or follows visual row order instead of the specified coordinate order. |
| 4. Destination packing | Agent treats `B:DQ` as ten 12-column slots, writes row-1 headers across all slots, packs blocks left-to-right ten per row, and processes sheets in `lap-1`, `lap-2`, `lap-9` order. | Preserves `etc...` examples as gold, invents a different row layout, leaves right-side columns blank, or mixes blocks from different source sheets in one row. |
| 5. Workbook delivery | Agent writes all three required completed workbooks under `outputs/`. | Reasoning may be correct but validator exits 2 due missing workbook paths. |

This case is high value only if the trace shows the agent dealing with the
semi-structured workbook layout. A simple PASS without inspecting the workbook
structure should be treated as suspicious and reviewed carefully.
