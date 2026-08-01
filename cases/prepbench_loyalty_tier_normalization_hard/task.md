# PrepBench Loyalty Tier Normalization Audit

This case is adapted from a real PrepBench data-preparation task. The source
data is a transaction-level retail dataset with product attributes and a loyalty
customer table. The business question here focuses on a narrower audit slice:
how much of canonical loyalty-tier profit comes from Gold customers after the
transaction, product, and loyalty tables are prepared consistently.

## Data

Read `data/README.md` first, then inspect the CSV files:

- `transactions.csv`: transaction rows, product ids, payment code, loyalty
  number, and sales before discount.
- `products.csv`: product attributes, unit cost, and selling price.
- `loyalty_customers.csv`: customer names, raw loyalty-tier strings, and
  discount values.

## Business Question

For transactions in calendar years 2023 and 2024, compute the share of total
canonical loyalty-tier profit contributed by Gold customers.

Report the share as a decimal rounded to 6 places. For example, report
`0.123456`, not `12.3456%`.

## Definitions

- Keep only transactions whose `Transaction_Date` falls in 2023 or 2024.
- Split `Product_ID` into product type, scent, and size using `-`.
  Replace underscores in the scent with spaces before joining to `products.csv`.
- In `products.csv`, use `Product_Size` when present; otherwise use `Pack_Size`
  as the product size join field.
- Normalize `Loyalty_Number` identifiers before joining. Values such as
  `1004721.0` and `1004721` refer to the same loyalty number.
- Normalize the raw loyalty-tier field by inspecting its observed values and
  mapping defensible values into exactly these canonical tiers: `Gold`,
  `Silver`, `Bronze`.
- Raw tier values that cannot be confidently mapped to one of the three
  canonical tiers should remain null and should not contribute to the
  canonical-tier denominator.
- Convert `Loyalty_Discount` from a percent string into a decimal rate.
- `Quantity = floor(Sales_Before_Discount / Selling_Price)`.
- Compute `Sales_After_Discount` only when `Loyalty_Number`,
  `Loyalty_Discount`, and `Sales_Before_Discount` are all present:
  `Sales_After_Discount = Sales_Before_Discount * (1 - Loyalty_Discount)`.
  Do not treat a missing `Loyalty_Discount` as `0%`, and do not impute a
  discount from the canonical tier.
- Compute `Profit = Sales_After_Discount - Unit_Cost * Quantity` only when
  `Sales_After_Discount`, `Unit_Cost`, and `Quantity` are all present.
- The denominator for the requested share is total non-null `Profit` across
  canonical `Gold`, `Silver`, and `Bronze` transaction rows only. Canonical-tier
  rows with missing discount still count as transaction rows and loyalty
  customers, but their null `Sales_After_Discount` and null `Profit` do not
  contribute to monetary sums.

## Working Rules

- Work only from `task.md`, `env.md`, and `data/`.
- Do not ask the user to resolve loyalty-tier values; inspect the field values
  and make a defensible normalization decision.
- Write helper scripts inside the current workspace if useful.

## Output Contract

Produce `answers.json`:

```json
{
  "answer": ["0.000000"]
}
```

After writing the file, report the final share and the output path.
