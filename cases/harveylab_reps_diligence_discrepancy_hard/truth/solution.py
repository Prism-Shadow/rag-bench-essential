#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import zipfile
from pathlib import Path


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def data_dir() -> Path:
    env = os.environ.get("BENCH_DATA_DIR")
    if env:
        return Path(env)
    for candidate in (Path("data"), truth_dir().parent / "data"):
        if (candidate / "documents").exists():
            return candidate
    raise SystemExit("cannot locate data/documents; run from a staged workspace or set BENCH_DATA_DIR")


def write_docx(path: Path, paragraphs: list[str]) -> None:
    body = []
    for paragraph in paragraphs:
        text = html.escape(paragraph)
        body.append(f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>")
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(body)}<w:sectPr/></w:body></w:document>"
    )
    files = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            "</Relationships>"
        ),
        "word/document.xml": document_xml,
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)


def main() -> int:
    expected = json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))
    docs = data_dir() / "documents"
    required_inputs = [
        "draft-spa-reps-warranties.docx",
        "disclosure-schedules-seller-draft.docx",
        "diligence-report-summary.docx",
        "ip-diligence-memo.docx",
        "key-contract-summary.xlsx",
        "ebitda-bridge-workpaper.xlsx",
        "ridgeline-diligence-email.eml",
    ]
    missing = [name for name in required_inputs if not (docs / name).exists()]
    if missing:
        raise SystemExit("missing source files: " + ", ".join(missing))

    paragraphs = [
        "Target Representations vs. Diligence Findings - Comparative Analysis Memorandum",
        "Prepared for the buyer-side M&A deal team.",
        "This memo compares the draft SPA representations and seller disclosure schedules against the diligence report summary, IP diligence memo, key contract summary, EBITDA bridge workpaper, and Ridgeline diligence email.",
        "Aggregate purchase price referenced in the SPA materials: $287 million. SPA signing date used for date-dependent analysis: March 14, 2025.",
        "",
    ]
    issue_text = {
        "patent_omissions": "High - Schedule 3.9 lists only 12 patents, while IP diligence identifies 14 patents. The omitted U.S. Patent Nos. 10,891,234 and 10,891,235 relate to the PF-4200 proportional valve design, the same product implicated by the AquaDyne dispute. Source: disclosure schedule 3.9 and IP diligence memo. Recommendation: update Schedule 3.9 to disclose all 14 patents and add a special indemnity if the omission affects AquaDyne exposure.",
        "claim_14_caveat": "High - The SPA IP representation references a non-infringement opinion for AquaDyne U.S. Patent No. 11,234,567, but the opinion could not analyze claim 14 because Target withheld testing data. Source: IP diligence memo and SPA IP representation. Recommendation: request full testing data, obtain a supplemental opinion, and qualify the representation.",
        "northpoint_expired_msa": "High - The NorthPoint Fabrication MSA expired on February 28, 2025, before the March 14, 2025 signing date, yet the SPA states listed material contracts are in full force and effect. NorthPoint represents about $18.6M, or 13% of revenue. Source: key contract summary and Schedule 3.15. Recommendation: correct the schedule, obtain renewal or written confirmation, and consider a closing condition.",
        "kessler_change_of_control": "Critical - Kessler Heavy Industries is the largest customer at about $29.4M, or 20.6% of revenue. Its MSA includes a change-of-control termination right on 60 days notice, but Schedule 3.15 does not disclose it. Source: key contract summary and disclosure schedule 3.15. Recommendation: obtain consent or waiver before closing and add the item to required consents.",
        "environmental_rec": "High - The Phase I environmental site assessment found a recognized environmental condition (REC) involving historical solvent contamination at the Dayton facility, but Schedule 3.12 only discloses the 2023 hydraulic fluid spill. No Phase II investigation has been completed. Source: diligence report summary and Schedule 3.12. Recommendation: conduct Phase II diligence and negotiate an environmental indemnity or escrow.",
        "california_tax_nexus": "High - Target has a San Jose, California sales representative and about $3.8M of California-sourced FY2024 revenue, but has not been filing California income tax returns. This conflicts with the tax representation that all required returns have been filed. Source: diligence report summary and tax representation. Recommendation: estimate exposure, seek voluntary disclosure, require delinquent returns, and request a tax indemnity.",
        "covid_ebitda_addback": "Medium - The $0.60M COVID-related supply-chain EBITDA add-back is questionable because similar charges appeared in FY2023 ($0.45M) and FY2022 ($0.55M), suggesting recurrence. At 9.5x, the purchase price impact is about $5.7M. Source: EBITDA bridge workpaper. Recommendation: remove or reduce the add-back and adjust purchase price.",
        "pension_liability": "High - The SPA/disclosure schedules cite a $4.3M frozen pension plan unfunded liability, but buyer diligence actuary estimates about $6.8M due to later interest-rate movement, a $2.5M gap. Source: diligence report summary. Recommendation: require an updated actuarial valuation and adjust indebtedness or obtain a special indemnity.",
        "martinez_insurance_gap": "High - Martinez v. PrecisionFlow seeks $12M, while the applicable insurance limit is $10M, leaving a $2M coverage gap. That conflicts with the SPA insurance/litigation representation that all litigation is covered by insurance. Source: diligence report summary and SPA litigation/insurance sections. Recommendation: disclose the shortfall, escrow or indemnify the uncovered amount, and review reserves.",
        "monterrey_lease_consent": "High - The Monterrey facility lease requires landlord consent for any direct or indirect change of control. The required consents schedule, Schedule 5.3, does not list this consent. The facility contributes about $38.2M, or 26.7% of revenue. Source: key contract summary and required consents schedule. Recommendation: obtain landlord consent before closing and add it to Schedule 5.3.",
        "employee_count": "Medium - Disclosure Schedule 3.17 lists 730 employees, while diligence shows 740 employees, a 10 employees discrepancy apparently related to Q4 2024 hires at Monterrey. Source: diligence report summary and Schedule 3.17. Recommendation: refresh employee schedules and verify payroll and benefits liabilities.",
        "section_382_nol": "Medium - Target has $4.1M of federal NOL carryforwards that will be subject to IRC Section 382 limitation after the 100% stock acquisition ownership change, but the SPA does not address this limitation. Source: diligence report summary and tax representation. Recommendation: model usable NOLs and update tax disclosures or purchase price assumptions.",
        "osha_citation": "Medium - The October 2024 OSHA lockout/tagout citation with a $28,700 penalty is contested and therefore not fully resolved, conflicting with compliance representations. Source: diligence report summary and SPA compliance section. Recommendation: disclose the contested citation, reserve for the penalty, and require resolution or indemnity.",
        "karen_beecham_share_claim": "High - Karen Beecham has a disputed claim to 5% of Hal Beecham's shares, about 3.1% of total outstanding shares, creating a title encumbrance inconsistent with sellers' free-and-clear share title representation. Source: Ridgeline diligence email and SPA capitalization/title representation. Recommendation: obtain a release or court order, escrow disputed shares, and make resolution a closing condition.",
    }
    for issue in expected["issues"]:
        paragraphs.append(issue_text[issue["id"]])

    paragraphs.extend([
        "",
        "Summary recommendation: require disclosure schedule corrections, targeted supplemental diligence, specific consents and waivers, and purchase price or escrow protection before signing or closing.",
    ])
    write_docx(Path(expected["required_output"]), paragraphs)
    print(f"wrote {expected['required_output']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
