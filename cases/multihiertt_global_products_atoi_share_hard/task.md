# MultiHiertt — Global Products ATOI share change

Source alignment: this is a **MultiHiertt-derived hard case** built from the
official MultiHiertt development split. The original benchmark question is kept
verbatim below. The agent-visible input is a document library rather than a
single preselected document, so first locate the relevant document and evidence,
then answer the original question.

## Data

`data/corpus.jsonl` is a MultiHiertt-style document library. Each JSONL row is
one document with paragraphs, HTML tables, and table descriptions. See
`data/README.md` for lineage, schema, and scale.

## Question

Original MultiHiertt question:

**what is the percentual growth of the global products' atoi concerning the total atoi for all segments during the years 2014-2015?**

## Answer guidelines

Report a single decimal number, not a percent string. Keep the benchmark's
original numeric scale.

Interpret "percentual growth ... concerning the total ATOI" as the absolute
change in Global Products' share of total reportable-segment ATOI from 2014 to
2015.

Do not compute the relative growth rate of that share.

Use the benchmark decimal scale: if a share changes from 10.0% to 10.5%,
report `0.005`, not `0.5`, `0.05`, or `5`.

## Working rules

- Work only from `task.md` and `data/`.
- Do not answer from memory or by using the upstream benchmark id.
- You may write helper scripts in the workspace.

## Output contract

Write **`<workspace-root>/answers.json`** in exactly this shape:

```json
{ "answer": ["..."] }
```

After writing `answers.json`, briefly report which document/evidence you used
and the calculation you performed.
