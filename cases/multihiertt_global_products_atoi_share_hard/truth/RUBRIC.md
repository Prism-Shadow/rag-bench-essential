# Rubric — MultiHiertt Global Products ATOI share change

Truth is isolated from the agent workspace. This file is for external audit of
answers and traces.

## Source

- Benchmark: MultiHiertt, development split
- UID: `76736e5cda684cd08c9f571d7f3976d9`
- Original question: `what is the percentual growth of the global products' atoi concerning the total atoi for all segments during the years 2014-2015?`
- Original answer: `0.00032`
- Original program: `divide(225,986), divide(224,983), subtract(#0,#1)`

## Required reasoning

| Dimension | Expected behavior | Common failure |
| --- | --- | --- |
| D1 document retrieval | Locate `doc_0024` from the 280-document corpus. | Search stops at a related ATOI document or a generic financial table. |
| D2 text evidence | Use total ATOI for all reportable segments: 2015 = 986, 2014 = 983. | Use 2016 total, total sales, or a company-wide figure from another section. |
| D3 table evidence | Use Global Rolled Products ATOI: 2015 = 225, 2014 = 224. | Use total sales or another row/segment. |
| D4 calculation | Compute `(225 / 986) - (224 / 983)` and round to `0.00032`. | Compute direct ATOI growth, direct subtraction, or return only one year's share. |
| D5 delivery | Write `answers.json` with `{ "answer": ["..."] }`. | Prints a value only, or exits without the required output file. |

## Gold evidence

- Paragraph 80: `ATOI for all reportable segments totaled $1,087 in 2016, $986 in 2015, and $983 in 2014.`
- Paragraph 84: `Global Rolled Products(1)`
- Table evidence ids: `3-6-2`, `3-6-3`

## Decoys

- `1` — subtracts 225 - 224.
- `0.0044642857` — computes 225 / 224 - 1.
- `0.2281947262` — returns 225 / 986 only.
- `0.2278738555` — returns 224 / 983 only.
- `0.0030518820` — computes total reportable-segment ATOI growth.
