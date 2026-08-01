# Review Subjectivity Metrics for Store-Catalogue Audits

Analytical-methods packet for app-review corpora. This packet is written for
analysts who need to select a scoring convention from a catalogue audit request,
inspect the available schema, and bind each numerical choice to a documented
method rather than to market-dashboard defaults.

The notes cover several related metrics. Only one of them applies to the
requested audit segment. Do not treat every number in this document as a scoring
constant.

## 1. Scope and units

The corpus used in catalogue audits usually contains two units:

1. A listing row, which describes how an app is represented in a store catalogue.
2. A review row, which describes a user comment and its model-derived sentiment
   fields.

These units are not interchangeable. A single app can appear in more than one
listing row because of category maintenance, export quirks, or historical
catalogue duplication. A review is still one review. Metrics over reviews must
not be multiplied by listing count unless the metric explicitly asks for listing
exposure.

The common join key is the app name. For audit metrics over app segments, first
define the app set from the catalogue table, then collect reviews whose app name
belongs to that app set. This avoids a join-multiplicity artifact in which every
review attached to a duplicated listing is counted multiple times.

## 2. Field reliability

Review sentiment exports typically include both polarity and subjectivity. A
finite subjectivity value means the sentiment model produced a subjectivity score
for that row. A `nan`, empty value, or unparsable token means the row has no
defined subjectivity for review-level subjectivity metrics.

For metrics in this packet:

- Polarity is used for direction-of-attitude scores.
- Subjectivity is used for opinion-load or emotional-language scores.
- Undefined subjectivity rows are excluded from subjectivity totals and counts.
- Undefined subjectivity rows are not converted to zero unless a metric
  explicitly defines an imputation step.

This distinction matters because subtracting a per-review reference from an
undefined row creates an artificial penalty.

## 3. Catalogue segment definitions

Catalogue segment membership is always determined at the app level before review
aggregation. The following definitions are used in different audit templates:

| segment name | app-level inclusion rule | common use |
| --- | --- | --- |
| Category segment | selected `Category` values | portfolio bucket reporting |
| Publisher segment | selected publisher identifiers when available | ownership analysis |
| Review-volume segment | apps with at least a volume floor | reliability screens |
| Multi-label genre segment | apps whose canonical genre metadata encodes more than one genre label | breadth audits |

For Google Play style exports, the canonical genre metadata is the `Genres`
field. A multi-label genre entry is encoded as a semicolon-delimited list of
genre labels in that field. In this export family, `Art & Design;Pretend Play`
is multi-label; `Tools` is not. The store `Category` field is a broader bucket
and is not a substitute for multi-label genre membership.

When an app has multiple listing rows, app membership is deduplicated by app name.
The segment is a set of apps, not a set of listing rows.

## 4. Metrics that do not apply to every audit

Several constants appear in methods notes because analysts reuse this packet
across tasks. They are listed here to reduce ambiguity.

| symbol | value | metric family | description |
| --- | ---: | --- | --- |
| alpha_p | 0.18 | polarity smoothing | market-neutral polarity offset used in direction scores |
| c_min | 30 | reliability filters | low-volume floor for dashboard charts |
| theta_s | 0.62 | alerting | high-subjectivity alert threshold |
| gamma_v | 1.25 | burst detection | short-window review-volume multiplier |
| rho_cov | 0.58 | coverage reports | typical market sentiment coverage ratio |
| eta_dup | 0.03 | listing QA | tolerated duplicate-listing audit rate |
| q_floor | 25 | sampling QA | minimum per-bucket sample request |
| beta_cat | 0.47 | category-normalized subjectivity | legacy category-reference score |

The presence of a constant in this table is not enough to use it. Select a
constant only when the requested metric family calls for it.

## 5. Directional polarity score

The directional polarity score is used when a task asks whether a segment is more
positive or negative than a market-neutral reference. It uses polarity values,
not subjectivity values:

```
DPS(S) = mean(p_i) - alpha_p
```

where `p_i` is the review polarity for a review in segment `S`, and `alpha_p` is
the polarity smoothing constant in the metric table. This metric does not answer
subjectivity-excess questions.

## 6. Category-normalized subjectivity

Category-normalized subjectivity compares a store category against a legacy
category reference. It is retained for compatibility with older dashboards:

```
CNS(C) = mean(s_i in category C) - beta_cat
```

It requires a category bucket as the target segment. It is not used when the task
asks for apps packaged across multiple content genres, because the unit there is
the multi-label genre app set, not a category bucket.

## 7. Catalogue breadth subjectivity excess

Breadth audits ask whether apps spanning more than one content genre carry more
opinion-loaded review language than a neutral single-genre reference. For this
task family, use the Multi-Genre Excess Subjectivity score, abbreviated MGES in
some notebooks:

```
MGES(S) = sum over valid reviews i in S of (s_i - b0)
```

where:

- `S` is the set of distinct apps in the multi-label genre segment;
- a review belongs to `S` if its `App` value is in that app set;
- `s_i` is the review's finite `Sentiment_Subjectivity` value;
- rows with undefined subjectivity are omitted from both the sum and the count;
- app-listing multiplicity must not multiply review rows.

The reference constant for this metric is the balanced single-genre review
control:

```
b0 = 0.42
```

This is a per-review constant. It is subtracted once for each valid review row in
the target segment. Do not subtract it once per app, once per category, or once
per listing row.

Equivalently, if `N` valid reviews in the target segment have subjectivity values
whose raw sum is `T`, then:

```
MGES = T - b0 * N
```

Report the final score as a single scalar rounded to two decimal places.

## 8. Listing exposure score

Listing exposure scores are used for catalogue QA rather than sentiment audits.
They intentionally count listing rows and may multiply app-level observations by
listing exposure. They are not review-subjectivity metrics:

```
LES(S) = listing_count(S) * eta_dup
```

Use this family only when the request asks about catalogue exposure, listing
maintenance, or duplicate-listing tolerance.

## 9. Sampling notes

When sample sizes are small, analysts may request a reliability floor. In that
case, `q_floor = 25` is a planning constant for sample requests. It is not a
subtraction reference. It does not alter a complete-corpus calculation unless the
task explicitly requests downsampling.

The Google Play export used in this audit family is treated as the complete
fixture for the requested task. Do not fetch additional reviews or fill missing
sentiment fields from outside sources.

## 10. Worked example with unrelated numbers

Suppose a category bucket has 40 valid reviews with polarity sum 12.0 and
subjectivity sum 21.0. A directional polarity request would compute:

```
12.0 / 40 - 0.18 = 0.12
```

A category-normalized subjectivity request would compute:

```
21.0 / 40 - 0.47 = 0.055
```

Neither calculation is an MGES calculation. For MGES, use the multi-label genre
app segment and subtract `b0` once per valid review.

## 11. Quality-control notes

The methods team reviews breadth-subjectivity reports for unit consistency. Most
failed reports mix catalogue-listing units with review-row units, or they import
a dashboard value from a market packet without checking the metric family. A good
report states enough provenance for another analyst to reconstruct the branch
selection, but it should not cite market context as if it were a methods rule.

## 12. Additional constants retained for older notebooks

The following table is retained because older notebooks in the same research
folder import it mechanically. Most constants are irrelevant unless a task names
the associated metric family.

| key | value | notes |
| --- | ---: | --- |
| window_7d | 7 | rolling release-window size |
| window_30d | 30 | monthly dashboard size |
| topk_topics | 15 | topic-model display cap |
| min_topic_mass | 0.04 | topic display suppression |
| polarity_alert_hi | 0.35 | positive burst display |
| polarity_alert_lo | -0.35 | negative burst display |
| subjectivity_alert_hi | 0.62 | emotional-language alert display |
| market_subjectivity_reference | 0.55 | copied from market packets for dashboard comparison |
| single_genre_control_breadth | 0.42 | MGES per-review reference |
| category_legacy_reference | 0.47 | legacy category normalization |
| sentiment_coverage_expected | 0.58 | market coverage reference |
| duplicate_listing_tolerance | 0.03 | catalogue QA reference |

If two constants look plausible, select by metric family and unit of analysis.
The unit test for MGES is simple: the reference must be per review, and the
target segment must be the multi-label genre app set.

## 13. Reporting format

Reports for this packet should state:

- the segment rule;
- the number of distinct apps in the segment;
- the number of valid review rows;
- the raw subjectivity sum;
- the method constant and source section;
- the rounded final scalar.

Evidence files should bind each step to a source. A final answer without source
binding is considered incomplete for audit use, even if the scalar happens to be
numerically correct.

## 14. Metric-selection decision log

The following notes are included because prior audit runs confused nearby metric
families. They are not additional tasks; they explain how to decide which branch
of the methods packet applies.

### 14.1 If the target is a store category

Use category-normalized subjectivity or a category-level polarity score only when
the requested segment is a `Category` bucket. A store category such as `FAMILY`
can contain many different genre labels, but the category itself is not the
multi-label genre segment. Category metrics average within a bucket. They usually
produce a mean-like value rather than a corpus-level excess total.

Common mistakes in this branch:

- selecting all rows with `Category = FAMILY` because many multi-label examples
  appear there;
- using `Category` count as the review count;
- subtracting a category reference from each app rather than from each valid
  review row.

### 14.2 If the target is a publisher or owner

Publisher metrics require a publisher identifier. The Google Play export used in
this fixture does not include a stable publisher field, so publisher metrics are
not available unless an external publisher map is explicitly supplied. Do not
infer publisher identity from app names.

### 14.3 If the target is a genre-breadth audit

Genre-breadth audits use the app's canonical genre metadata to define the app
set. The phrase "packaged across more than one content genre" maps to the
multi-label genre segment. Once that app set is identified, all aggregation is
over review rows for those apps.

The scoring branch is therefore:

```
catalogue metadata -> distinct app segment -> review rows -> finite subjectivity -> per-review excess total
```

The branch is not:

```
catalogue rows -> listing-expanded join -> listing-weighted review total
```

## 15. Extended constant register

This register collects constants from older notebooks, dashboards, and sampling
procedures. It is intentionally noisy. Use the metric family and unit of analysis
to decide relevance.

| constant | value | unit | common source |
| --- | ---: | --- | --- |
| alpha_p | 0.18 | polarity points per review | polarity dashboard |
| alpha_p_alt | 0.20 | polarity points per review | older polarity dashboard |
| beta_cat | 0.47 | subjectivity points per review | category-normalized subjectivity |
| beta_cat_family | 0.49 | subjectivity points per review | legacy family-category report |
| beta_cat_game | 0.44 | subjectivity points per review | legacy game-category report |
| b0 | 0.42 | subjectivity points per valid review | MGES single-genre control |
| b0_low_volume | 0.40 | subjectivity points per valid review | deprecated low-volume pilot |
| b0_high_volume | 0.43 | subjectivity points per valid review | deprecated high-volume pilot |
| theta_s | 0.62 | subjectivity threshold | alerting dashboards |
| theta_s_soft | 0.57 | subjectivity threshold | soft alert experiment |
| market_subjectivity_reference | 0.55 | subjectivity points per review | market packet |
| rho_cov | 0.58 | fraction of rows | sentiment coverage reports |
| rho_cov_strict | 0.51 | fraction of rows | strict parser coverage reports |
| gamma_v | 1.25 | volume multiplier | release burst detection |
| gamma_v_long | 1.10 | volume multiplier | long-window burst detection |
| eta_dup | 0.03 | duplicate-listing fraction | catalogue QA |
| eta_dup_alert | 0.05 | duplicate-listing fraction | catalogue QA alert |
| q_floor | 25 | sample rows | sampling QA |
| c_min | 30 | sample rows | low-volume dashboard suppression |
| topic_mass_min | 0.04 | topic share | topic display |
| topic_mass_review | 0.08 | topic share | review-topic display |
| neutral_band_low | -0.05 | polarity points | neutrality band |
| neutral_band_high | 0.05 | polarity points | neutrality band |

The constants most often confused with the MGES reference are 0.55, 0.47, and
0.62. The correct branch for a breadth subjectivity excess total uses the
single-genre control `b0`, because the calculation subtracts a per-review
neutral-reference subjectivity from each valid review in the target segment.

## 16. Parser notes for Google Play exports

The export lineage uses conventional CSV strings. Analysts should inspect raw
values before writing code. Relevant observations:

- App names are strings and should be treated as case-sensitive join keys within
  this fixture.
- `Genres` is a string field. Multi-label entries use a delimiter inside the
  field rather than multiple catalogue rows.
- Empty translated reviews may still have empty sentiment fields; do not infer a
  score from the text field when the numeric subjectivity field is unavailable.
- Some app names appear in reviews even if the listing table has duplicate rows.
  Deduplicate the app segment before collecting reviews.

Do not normalize genre labels by splitting on ampersands, spaces, or words such
as "and". The export's multi-label marker is the delimiter used by the store
genre metadata itself.

## 17. Review-row validity details

For subjectivity metrics, a valid review row has a finite numeric
`Sentiment_Subjectivity`. The following are invalid:

- literal `nan`;
- empty string;
- missing field;
- non-numeric strings.

Invalid rows are excluded before both the raw subjectivity total and the
per-review reference subtraction are computed. Treating invalid subjectivity as
zero changes the unit of analysis from "valid review rows" to "all review rows"
and creates a false negative excess because the reference is still subtracted.

For polarity metrics, use `Sentiment_Polarity` instead. Do not mix polarity and
subjectivity fields.

## 18. Implementation caution

Implementation should follow the metric branch selected above, but the packet
does not prescribe a programming language or query engine. Analysts commonly use
SQL, Python, or spreadsheet pivots. Whatever tool is used, the report should make
the branch selection auditable: name the app segment, the review-score field, the
reference constant's method family, and the aggregation unit.

## 19. Historical notes on deprecated branches

Early notebooks attempted to estimate genre breadth by counting how many store
categories an app appeared in. That branch was removed because catalogue
maintenance can create duplicate rows unrelated to product breadth. The current
genre-breadth branch uses the canonical genre metadata field instead.

Another deprecated notebook imputed missing subjectivity as zero. That imputation
was removed because no-subjectivity rows are not neutral observations; they are
unscored observations. The current methods exclude them from subjectivity
metrics.

Finally, some market dashboards used the cross-vendor subjectivity average as a
visual reference line. That visual reference remains useful for market slides,
but formal breadth-excess scores use the single-genre control defined in the
methods branch.
