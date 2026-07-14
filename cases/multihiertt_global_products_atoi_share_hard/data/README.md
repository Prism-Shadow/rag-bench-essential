# Data README

## Source

This payload is derived from the official MultiHiertt development split
(*MultiHiertt: Numerical Reasoning over Multi Hierarchical Tabular and Textual
Data*, ACL 2022; official repository:
`https://github.com/psunlpgroup/MultiHiertt`).

The agent-visible corpus keeps the benchmark-style document content needed for
the public question and omits private QA metadata and programs.

## Files

- `corpus.jsonl` — 280 unique MultiHiertt development documents, one JSON object
  per line.

Each row has this schema:

```json
{
  "doc_key": "doc_0000",
  "paragraphs": ["..."],
  "tables_html": ["<table>...</table>"],
  "table_descriptions": {
    "0-0-0": "Table ... shows ...",
    "...": "..."
  }
}
```

## Scale

- Documents: 280
- File size: about 8.7 MB
- Total document text/table-description content: about 8.2 million characters

The relevant question requires locating a document in the library and combining
text evidence with table evidence.
