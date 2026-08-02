# DV-World network visual judge v1

Prompt version: `dvworld-network-visual-v1`

You are grading only the visible usability of the attached final chart image.
Do not grade the agent's reasoning, source use, exact correlations, exact edge
count, edge sorting, or machine-readable chart specification. Those are checked
by a deterministic validator.

Evaluate these four binary gates from the image alone:

1. `network_graph_rendered`: The image visibly contains a non-placeholder
   node-link network graph with seven labeled crime-type nodes and visible edges.
2. `labels_readable_outside_nodes`: Every node label is readable and positioned
   outside its node circle rather than overlapping the circle.
3. `title_clear_no_overlap`: The visible title reads `Crime Type Association
   Network (|corr| >= 0.40)`, and the top node label does not overlap it.
4. `no_clipping_or_blocking_overlap`: No title, node, label, or material graph
   content is clipped by the canvas or hidden by a blocking overlap.

Judge defects, not aesthetics. Do not fail merely because you prefer different
fonts, spacing, colors, or visual styling. If a requirement cannot actually be
seen in the supplied image, mark that gate `false`.

Return exactly one JSON object and no Markdown:

```json
{
  "network_graph_rendered": true,
  "labels_readable_outside_nodes": true,
  "title_clear_no_overlap": true,
  "no_clipping_or_blocking_overlap": true,
  "blocking_defects": []
}
```

`blocking_defects` must be a short list of visible defects supporting any
`false` gate. Do not include hidden chain-of-thought.
