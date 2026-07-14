# Trace Rubric

| Step | What to Check | Silent Failure |
| --- | --- | --- |
| Image handling | Agent opens, OCRs, or crops `data/document_page.jpg`. | Treats the task as text-only and guesses. |
| Field binding | Agent binds the answer to the printed label `Contract Effective Date`. | Reads the nearby `Date Contract Signed` field. |
| OCR skepticism | Agent notices OCR ambiguity in the handwritten area and uses visual/crop confirmation. | Trusts noisy OCR such as malformed dates without checking the image. |
| Evidence | `evidence.json` includes image path, field label, and a plausible pixel bbox. | Evidence only says "from OCR" with no region or label. |
| Delivery | `answers.json`, `evidence.json`, and `report.md` are present at workspace root. | Correct date appears only in final message. |
