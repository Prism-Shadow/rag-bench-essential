# Data Dictionary - App Store Analytical Sources

This directory contains a small heterogeneous source set:

- structured catalogue/review tables exported from a Google Play app corpus;
- unstructured documents used by analysts when defining review-audit metrics.

The table schemas below describe fields only. The task-specific scoring method is
defined in the documents under `docs/`.

## Structured data

### `playstore.csv`

One row per app listing. Some apps may appear in more than one listing row.

| column | meaning |
| --- | --- |
| `App` | application name; join key to `user_reviews.csv` |
| `Category` | store category bucket, e.g. `ART_AND_DESIGN` |
| `Rating`, `Reviews`, `Size`, `Installs`, `Type`, `Price`, `Content Rating` | listing attributes |
| `Genres` | raw genre metadata from the store export; values may encode one or more genre labels |
| `Last Updated`, `Current Ver`, `Android Ver` | versioning metadata |

### `user_reviews.csv`

One row per user review. A review belongs to an app through `App`.

| column | meaning |
| --- | --- |
| `App` | application name; join key to `playstore.csv` |
| `Translated_Review` | review text, sometimes empty |
| `Sentiment` | `Positive` / `Negative` / `Neutral` / empty |
| `Sentiment_Polarity` | numeric polarity, or `nan` when unavailable |
| `Sentiment_Subjectivity` | numeric subjectivity, or `nan` when unavailable |

## Documents

- `docs/methodology_review.md` - research/method notes for review-audit scoring.
- `docs/market_report.md` - market context and descriptive statistics.

Read both. They serve different roles in the source packet.
