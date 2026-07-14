# Data lineage — NSCG 2023 (LongDA)

- **Benchmark**: LongDA (arXiv:2601.02598), survey folder `NSCG`.
- **Upstream source**: NSF NCSES, 2023 National Survey of College Graduates,
  public-use file. Public domain (U.S. government data). Published reference:
  NSF 25-331.
- **Scale**:
  - `epcg23.csv` — ~144 MB, thousands of columns, one row per respondent
    (~94,600 respondents).
  - `docs/Dpcg23.xlsx` — data dictionary (variable → description).
  - `docs/Ppcg23.html` / `docs/Ppcg23.pdf` — codebook with response categories and
    value codes.
  - `docs/2023-NSCG-21_annotated_7Aug25.pdf` — annotated questionnaire.
  - `docs/2023NSCG_RecodeDocumentation_4Feb25.pdf` — recode documentation.

## Cautions

- The data file has thousands of columns; read only the columns you need rather
  than loading it whole.
- Documentation is provided as a `.xlsx` data dictionary, `.html`/`.pdf` codebooks,
  and PDFs; extract text (e.g. `pdftotext`, `PyPDF2`, an xlsx/HTML reader) before
  searching.

## Re-fetch

```bash
huggingface-cli download Yiyang-Ian-Li/LongDA --repo-type dataset \
  --include 'NSCG/*' --local-dir <dest>
# or curl files under:
#   https://huggingface.co/datasets/Yiyang-Ian-Li/LongDA/resolve/main/NSCG/...
```
