# Data Dictionary - PrepBench Loyalty Tier Normalization

This directory contains public input tables adapted from a PrepBench multi-table
transaction preparation problem, renamed for readability. The original task
involves product attributes, loyalty customers, discounts, quantity, sales after
discount, and profit.

## Scale

- `transactions.csv`: 105,495 rows plus header.
- `loyalty_customers.csv`: 9,789 rows plus header.
- `products.csv`: 60 rows plus header.

## Files

### `transactions.csv`

One row per purchased product line.

| column | meaning |
| --- | --- |
| `Transaction_Date` | transaction date as a weekday/month string |
| `Transanction_Number` | transaction identifier; source column name preserved |
| `Product_ID` | compound product key: product type, scent, and size |
| `Cash_or_Card` | payment code (`1` card, `2` cash) |
| `Loyalty_Number` | customer loyalty identifier, sometimes represented as a float string |
| `Sales_Before_Discount` | sales value before loyalty discount |

### `products.csv`

Product lookup table.

| column | meaning |
| --- | --- |
| `Product_Type` | product type, such as bar or liquid |
| `Product_Scent` | product scent label |
| `Pack_Size` | pack size fallback |
| `Product_Size` | product size when populated |
| `Unit_Cost` | unit cost for profit calculation |
| `Selling_Price` | selling price used to derive quantity |

### `loyalty_customers.csv`

Customer lookup table.

| column | meaning |
| --- | --- |
| `Loyalty_Number` | customer loyalty identifier |
| `Customer_Name` | source name in `last, first` order |
| `Loyalty_Tier` | raw tier label; inspect the observed values before using it |
| `Loyalty_Discount` | discount as a percent string |

## Note

As with the other fields in this data-preparation task, inspect the observed
values of `Loyalty_Tier` before using it in calculations.
