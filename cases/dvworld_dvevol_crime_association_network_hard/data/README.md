# Data Notes

Lineage: DV-World visualization-edit task over an FBI crime table. The original
public edit prompt is preserved as `source_task.md`; the original source image is
preserved as `source_fig.png`.

Files:

- `data_new.xlsx`: one Excel workbook, sheet `Sheet1`, about 214 rows by
  23 columns when read without promoting the multi-row header.
- `source_fig.png`: source visualization context supplied by the benchmark.
- `source_task.md`: public chart-edit instruction.

Caution:

- The workbook is semi-structured. The first visible rows are title/header rows,
  and the actual data rows begin later.
- The useful fields are alternating count/rate columns. The required network
  uses only the seven crime `*_Rate` fields for 2016.
- The workbook contains aggregate region/division rows and percent-change rows;
  these are not state-level crime observations.
