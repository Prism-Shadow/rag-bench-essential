# Rubric: DV-World Network Association Graph

Only the two final chart artifacts are scored:

1. `chart_spec.json` is checked deterministically for the complete node/edge
   semantics, correlations, filtering, bins, widths, colors, and fixed layout.
2. `figure.png` is judged visually for actual rendering, readable outside-node
   labels, title separation, and freedom from clipping or blocking overlap.

Both are hard gates for official PASS. The visual judge does not evaluate exact
edge counts, numeric correlations, or artistic taste; those belong to the
deterministic validator. Trace, helper scripts, and intermediate tables are not
scored. The versioned visual prompt is `vision_judge_prompt.md`.
