# Rubric: BankerToolBench CAKE LBO Sensitivity

Score the three requested final artifacts independently:

- the Excel workbook contains the required sensitivity tables, axes, and values;
- the two-slide presentation contains the required summary content;
- the PDF is a readable export of the presentation.

The workbook, PPTX, and PDF receive deterministic checks. The submitted PDF is
also rendered with a command-line PDF renderer and judged visually for blocking
delivery defects: missing/non-blank pages, visibly present tables and discussion
content, readability, clipping, overlap, and broken rendering.

Official PASS requires all deterministic artifact checks and the visual gate.
The visual judge does not recompute financial values or grade aesthetic taste.
The reasoning process, editing method, trace, and helper files are not scored.
The versioned visual prompt is `vision_judge_prompt.md`.
