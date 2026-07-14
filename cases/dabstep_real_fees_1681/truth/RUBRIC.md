# Rubric - DABstep Applicable Fee IDs

Truth is isolated from the agent workspace. This file is for external answer and
trace audit.

## Required Reasoning

| Dimension | Expected behavior | Common failure |
| --- | --- | --- |
| D1 task scope | Select merchant `Belles_cookbook_store`, year 2023, day-of-year 10. | Uses all days, the wrong merchant, or a calendar date conversion mistake. |
| D2 merchant profile | Use merchant attributes from `merchant_data.json`: account type, MCC, capture delay, and acquirer. | Infers merchant profile from transactions only or ignores capture delay. |
| D3 monthly metrics | Compute January monthly volume and fraud percentage from the merchant's 2023 payments. | Uses day-only volume, all-merchant volume, count-based fraud, or a different month. |
| D4 rule matching | Apply every `fees.json` condition: card scheme, account type, capture delay, monthly fraud, monthly volume, MCC, credit flag, ACI, and intracountry. | Treats empty lists as no match, ignores null-as-wildcard, or mishandles `k`/`m`/`%` ranges. |
| D5 transaction aggregation | Return the union of fee IDs matching at least one day-10 transaction. | Returns one transaction's fees only or includes duplicate IDs. |
| D6 delivery | Write `answers.json` with `{ "answer": ["<comma-separated fee ids>"] }`. | Prints the list only or writes a different schema. |

## Gold

- Applicable fee IDs as an unordered set: `741, 709, 454, 813, 381, 536, 473, 572, 477, 286`.
- The validator compares unordered ID sets, not list order.

## Decoys

- Using only rounded or visible row-level quantities instead of the natural-month
  fraud/volume metrics.
- Treating empty list fields in `fees.json` as empty eligibility rather than
  wildcard eligibility.
- Applying capture-delay strings literally without interpreting `<3`, `3-5`,
  `>5`, `manual`, and `immediate`.
