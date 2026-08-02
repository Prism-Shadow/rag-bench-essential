# BankerToolBench CAKE PDF visual judge v1

Prompt version: `banker-cake-pdf-visual-v1`

You are grading only blocking visual defects in the attached two rendered PDF
pages. Do not grade the agent's reasoning, recompute IRR values, verify exact
axes, or inspect the underlying workbook/PPTX structure. Those are checked by a
deterministic validator.

Evaluate these five binary gates from the rendered pages alone:

1. `two_nonblank_pages`: Two distinct, substantially non-blank presentation
   pages are visible.
2. `all_four_tables_visibly_present`: Across the two pages, four sensitivity
   tables are visibly present: Entry Share Price Premium, Term Loan Leverage,
   Revenue Growth, and COGS, each versus Exit Multiple.
3. `discussion_content_visibly_present`: Each table has nearby visible
   discussion/bullet content, and each page has a visible headline and source
   footnote area.
4. `headlines_and_discussion_are_substantive`: Each page headline states a
   conclusion rather than only naming the topic, and each of the four tables has
   approximately 3-4 meaningful conclusion/insight bullets rather than filler.
5. `tables_and_text_readable`: Table labels, axis values, IRR cells, headlines,
   and discussion text are legible at normal full-page viewing resolution.
6. `no_clipping_overlap_or_broken_render`: No material table, headline, bullet,
   or footnote is clipped, hidden by overlap, off-canvas, or replaced by a
   broken/missing object.

Judge defects, not aesthetics. Do not fail for subjective preferences about
fonts, colors, spacing, or design style when the content remains usable. If a
requirement cannot actually be seen, mark that gate `false`.

Return exactly one JSON object and no Markdown:

```json
{
  "two_nonblank_pages": true,
  "all_four_tables_visibly_present": true,
  "discussion_content_visibly_present": true,
  "headlines_and_discussion_are_substantive": true,
  "tables_and_text_readable": true,
  "no_clipping_overlap_or_broken_render": true,
  "blocking_defects": []
}
```

`blocking_defects` must be a short list of visible defects supporting any
`false` gate. Do not include hidden chain-of-thought.
