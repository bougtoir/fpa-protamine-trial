#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "literature" / "raw"
CSV_PATH = ROOT / "references_verified.csv"
JSON_PATH = ROOT / "output" / "references_vancouver.json"
LEDGER_PATH = ROOT / "source" / "source_acquisition.csv"

DOI_REFERENCES = [
    {
        "id": "boer2018",
        "doi": "10.1016/j.bja.2018.01.023",
        "claim": "Protamine pharmacology, anticoagulant effects, dosing, and adverse reactions",
    },
    {
        "id": "weiler1990",
        "doi": "10.1016/0091-6749(90)90189-b",
        "claim": "Prospective incidence and risk factors for immediate protamine reactions",
    },
    {
        "id": "kimmel1998events",
        "doi": "10.1016/s0895-4356(97)00241-2",
        "claim": "12.9% rate of adverse events after protamine and under-reporting",
    },
    {
        "id": "welsby2005",
        "doi": "10.1097/00000542-200502000-00011",
        "claim": "Dose-duration protamine haemodynamic perturbations and mortality association",
    },
    {
        "id": "kimmel1998risk",
        "doi": "10.1016/s0735-1097(98)00484-7",
        "claim": "NPH insulin and allergy risk factors for clinically important protamine events",
    },
    {
        "id": "weiss1989",
        "doi": "10.1056/nejm198904063201402",
        "claim": "Protamine antibodies and life-threatening reactions after protamine-insulin exposure",
    },
    {
        "id": "suksompong2023",
        "doi": "10.21037/apm-22-714",
        "claim": "Randomised antihistamine pretreatment trial and serial haemodynamic measurement",
    },
    {
        "id": "hobbhahn1988",
        "doi": "10.1213/00000539-198803000-00008",
        "claim": "Preclinical cyclooxygenase inhibition attenuated protamine haemodynamic responses",
    },
    {
        "id": "wang2021",
        "doi": "10.1038/s41392-020-00443-w",
        "claim": "Arachidonic-acid and cyclooxygenase pathway biology",
    },
    {
        "id": "yamashita2006",
        "doi": "10.1007/s00540-006-0389-6",
        "claim": "Clinical perioperative use of intravenous flurbiprofen axetil",
    },
    {
        "id": "liu2024",
        "doi": "10.1186/s13741-024-00419-2",
        "claim": "Observational perioperative flurbiprofen and acute kidney injury evidence",
    },
    {
        "id": "sts2018",
        "doi": "10.1016/j.athoracsur.2017.09.061",
        "claim": "Cardiopulmonary-bypass heparin and protamine dosing recommendations",
    },
    {
        "id": "vonk2014",
        "doi": "10.1053/j.jvca.2013.09.007",
        "claim": "Individualised protamine management and postoperative haemostasis",
    },
    {
        "id": "wesselink2018",
        "doi": "10.1016/j.bja.2018.04.036",
        "claim": "Heterogeneity and outcome associations of perioperative hypotension definitions",
    },
    {
        "id": "sessler2019",
        "doi": "10.1016/j.bja.2019.01.013",
        "claim": "MAP 60–70 mmHg absolute threshold and duration-dependent organ risk",
    },
    {
        "id": "kdigo2012",
        "doi": "10.1038/kisup.2012.1",
        "claim": "KDIGO acute kidney injury definition and staging",
    },
    {
        "id": "spirit2025",
        "doi": "10.1136/bmj-2024-081477",
        "claim": "Current protocol reporting guideline",
    },
    {
        "id": "consort2025",
        "doi": "10.1136/bmj-2024-081123",
        "claim": "Current randomised-trial results reporting guideline",
    },
]

MANUAL_REFERENCES = [
    {
        "id": "source2026",
        "authors": "Onishi T, Ikenoue T",
        "title": "Association between intravenous flurbiprofen axetil pre-administration and attenuation of protamine-induced hypotension in cardiovascular surgery: a retrospective cohort study",
        "journal": "J Jpn Soc Clin Anesth",
        "year": "2026",
        "volume": "46",
        "issue": "5",
        "pages": "413-427",
        "doi": "",
        "pmid": "",
        "url": "",
        "claim": "Hypothesis-generating retrospective signal; local source is author manuscript, not independently verified publisher PDF",
        "verification_status": "Bibliographic citation supplied by author; numeric content verified against supplied manuscript",
    },
    {
        "id": "ropion_label",
        "authors": "Kaken Pharmaceutical Co Ltd",
        "title": "Ropion intravenous 50 mg: Japanese package insert",
        "journal": "",
        "year": "2024",
        "volume": "",
        "issue": "",
        "pages": "",
        "doi": "",
        "pmid": "",
        "url": "https://pins.japic.or.jp/pdf/newPINS/00054017.pdf",
        "claim": "Japanese indication, 50-mg dose, composition, contraindications, and safety warnings",
        "verification_status": "Official Japanese electronic package insert saved locally",
    },
    {
        "id": "protamine_jp_label",
        "authors": "Mochida Pharmaceutical Co Ltd",
        "title": "Protamine sulfate intravenous 100 mg: Japanese package insert",
        "journal": "",
        "year": "2023",
        "volume": "",
        "issue": "",
        "pages": "",
        "doi": "",
        "pmid": "",
        "url": "https://pins.japic.or.jp/pdf/newPINS/00063579.pdf",
        "claim": "Japanese protamine dose limit, dilution, infusion duration, and warnings",
        "verification_status": "Official Japanese electronic package insert saved locally",
    },
    {
        "id": "fda_nsaid_label",
        "authors": "US Food and Drug Administration",
        "title": "Diclofenac sodium (Cambia) prescribing information: boxed warning for cardiovascular, gastrointestinal, and CABG risks",
        "journal": "",
        "year": "2024",
        "volume": "",
        "issue": "",
        "pages": "",
        "doi": "",
        "pmid": "",
        "url": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/022165s016lbl.pdf",
        "claim": "International NSAID class warning and CABG contraindication; not a flurbiprofen-axetil-specific label",
        "verification_status": "Official FDA label",
    },
]

PUBLIC_SOURCES = {
    "aca_information_for_authors_20260925.html": {
        "url": "https://journals.lww.com/aoca/pages/informationforauthors.aspx",
        "version": "Live page captured 2026-09-25",
        "conditions": "Captured through browser because direct request was blocked by Cloudflare",
        "usage": "Public journal instructions; retain snapshot for audit",
    },
    "ropion_if_202410.pdf": {
        "url": "https://medical-pro.kaken.co.jp/product/ropion/documents/ropion_if_202410.pdf",
        "version": "October 2024 interview form",
        "conditions": "Medical-professional acknowledgement completed in browser; then downloaded",
        "usage": "Public manufacturer professional information; citation/quotation only",
    },
    "ropion_japan_package_insert.pdf": {
        "url": "https://pins.japic.or.jp/pdf/newPINS/00054017.pdf",
        "version": "Retrieved live version 2026-09-25",
        "conditions": "Direct HTTPS download",
        "usage": "Public official package insert; citation/quotation only",
    },
    "protamine_japan_package_insert.pdf": {
        "url": "https://pins.japic.or.jp/pdf/newPINS/00063579.pdf",
        "version": "Retrieved live version 2026-09-25",
        "conditions": "Direct HTTPS download",
        "usage": "Public official package insert; citation/quotation only",
    },
    "sts_sca_amsect_anticoagulation_guideline.html": {
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5850589/",
        "version": "PMC full-text snapshot",
        "conditions": "Direct HTTPS download",
        "usage": "Open-access article under source-stated terms",
    },
    "spirit_2025_expanded_checklist.pdf": {
        "url": "https://www.consort-spirit.org/_files/ugd/b5740e_ffb985d849cc41afbe66d58babc8653f.pdf",
        "version": "SPIRIT 2025 expanded checklist",
        "conditions": "Direct HTTPS download",
        "usage": "Reporting-guideline checklist; retain for completion audit",
    },
    "spirit_2025_statement_20260925.html": {
        "url": "https://www.bmj.com/content/389/bmj-2024-081477",
        "version": "Live article page captured 2026-09-25",
        "conditions": "Captured through browser because direct request was blocked",
        "usage": "Public article page; citation/quotation under publisher terms",
    },
    "consort_2025_statement_20260925.html": {
        "url": "https://www.bmj.com/content/389/bmj-2024-081123",
        "version": "Live article page captured 2026-09-25",
        "conditions": "Captured through browser because direct request was blocked",
        "usage": "Public article page; citation/quotation under publisher terms",
    },
    "dailymed_protamine.html": {
        "url": "https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=8df0a819-9e1a-44ce-97a6-3ea82c867d44",
        "version": "Live DailyMed label snapshot",
        "conditions": "Direct HTTPS download",
        "usage": "US government drug-label information",
    },
    "suksompong_2022_antihistamine_trial.html": {
        "url": "https://apm.amegroups.org/article/view/106570/html",
        "version": "Publisher full-text snapshot",
        "conditions": "Direct HTTPS download",
        "usage": "Open-access article under source-stated terms",
    },
    "kimmel_1998_protamine_adverse_events.html": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "version": "Browser capture attempted for Kimmel adverse-event article",
        "conditions": "Browser capture resolved to a PubMed landing page rather than article full text",
        "usage": "Retained as an incomplete acquisition attempt; not used as the metadata source",
    },
    "ropion_if_202410_browser.html": {
        "url": "https://medical-pro.kaken.co.jp/auth.html",
        "version": "Medical-professional authentication page capture",
        "conditions": "Browser capture before retrieving the interview-form PDF",
        "usage": "Authentication provenance only; not substantive evidence",
    },
}

REFERENCE_OVERRIDES = {
    "hobbhahn1988": {
        "pages": "253-260",
        "journal": "Anesth Analg",
    },
    "kdigo2012": {
        "authors": "Kidney Disease: Improving Global Outcomes Acute Kidney Injury Work Group",
        "title": "KDIGO clinical practice guideline for acute kidney injury",
        "journal": "Kidney Int Suppl",
        "year": "2012",
        "volume": "2",
        "issue": "1",
        "pages": "1-138",
        "doi": "",
        "url": "https://kdigo.org/guidelines/acute-kidney-injury/",
        "verification_status": "Official KDIGO guideline citation",
    },
}


def clean(value: str) -> str:
    return html.unescape(
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", value))
    ).strip()


def crossref_record(reference: dict[str, str]) -> dict[str, str]:
    doi = reference["doi"]
    path = RAW_DIR / f"crossref_{reference['id']}.json"
    if not path.exists():
        response = requests.get(
            f"https://api.crossref.org/works/{quote(doi, safe='')}",
            timeout=60,
            headers={"User-Agent": "IF-U-PLEASE-II-protocol/1.0 (mailto:bougtoir@gmail.com)"},
        )
        response.raise_for_status()
        path.write_bytes(response.content)
    message = json.loads(path.read_text(encoding="utf-8"))["message"]
    authors = []
    for author in message.get("author", []):
        family = clean(author.get("family", ""))
        given = "".join(
            part[0]
            for part in re.split(r"[\s-]+", clean(author.get("given", "")))
            if part
        )
        authors.append(f"{family} {given}".strip())
    issued = message.get("published-print") or message.get("published-online") or message.get("issued")
    year = str(issued["date-parts"][0][0]) if issued else ""
    record = {
        "id": reference["id"],
        "authors": ", ".join(authors),
        "title": clean(message.get("title", [""])[0]),
        "journal": clean(message.get("container-title", [""])[0]),
        "year": year,
        "volume": clean(message.get("volume", "")),
        "issue": clean(message.get("issue", "")),
        "pages": clean(message.get("page", message.get("article-number", ""))),
        "doi": doi.lower(),
        "pmid": "",
        "url": f"https://doi.org/{doi}",
        "claim": reference["claim"],
        "verification_status": "Metadata retrieved from Crossref DOI record",
    }
    record.update(REFERENCE_OVERRIDES.get(reference["id"], {}))
    return record


def vancouver(record: dict[str, str]) -> str:
    authors = record["authors"].split(", ")
    if len(authors) > 6:
        author_text = ", ".join(authors[:6]) + ", et al"
    else:
        author_text = record["authors"]
    citation = f"{author_text}. {record['title']}."
    if record["journal"]:
        citation += f" {record['journal']}."
    if record["year"]:
        citation += f" {record['year']}"
    if record["volume"]:
        citation += f";{record['volume']}"
        if record["issue"]:
            citation += f"({record['issue']})"
    if record["pages"]:
        citation += f":{record['pages']}"
    citation += "."
    if record["doi"]:
        citation += f" doi:{record['doi']}."
    elif record["url"]:
        citation += f" Available from: {record['url']}."
    return re.sub(r"\.\.", ".", citation)


def make_ledger() -> None:
    rows = []
    existing_timestamps = {}
    if LEDGER_PATH.exists():
        with LEDGER_PATH.open(encoding="utf-8", newline="") as handle:
            existing_timestamps = {
                row["local_path"]: row["retrieved_utc"]
                for row in csv.DictReader(handle)
            }

    def retrieved_utc(path: Path) -> str:
        local_path = str(path.relative_to(ROOT))
        return existing_timestamps.get(
            local_path,
            datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
        )

    public_dir = ROOT / "source" / "public"
    for filename, metadata in PUBLIC_SOURCES.items():
        path = public_dir / filename
        if not path.exists():
            raise FileNotFoundError(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(
            {
                "source_type": "public",
                "identifier": metadata["version"],
                "url": metadata["url"],
                "retrieved_utc": retrieved_utc(path),
                "retrieval_conditions": metadata["conditions"],
                "local_path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": digest,
                "usage_conditions": metadata["usage"],
            }
        )
    for reference in DOI_REFERENCES:
        path = RAW_DIR / f"crossref_{reference['id']}.json"
        if not path.exists():
            raise FileNotFoundError(path)
        rows.append(
            {
                "source_type": "public-api",
                "identifier": reference["doi"],
                "url": f"https://api.crossref.org/works/{quote(reference['doi'], safe='')}",
                "retrieved_utc": retrieved_utc(path),
                "retrieval_conditions": "Crossref REST API; complete single-work response",
                "local_path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "usage_conditions": "Crossref public metadata; retain response for citation audit",
            }
        )
    with LEDGER_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    records = [MANUAL_REFERENCES[0]]
    for reference in DOI_REFERENCES:
        records.append(crossref_record(reference))
    records.extend(MANUAL_REFERENCES[1:])
    order = [
        "source2026",
        "boer2018",
        "weiler1990",
        "kimmel1998events",
        "welsby2005",
        "kimmel1998risk",
        "weiss1989",
        "suksompong2023",
        "hobbhahn1988",
        "wang2021",
        "ropion_label",
        "yamashita2006",
        "liu2024",
        "fda_nsaid_label",
        "sts2018",
        "vonk2014",
        "protamine_jp_label",
        "wesselink2018",
        "sessler2019",
        "kdigo2012",
        "spirit2025",
        "consort2025",
    ]
    by_id = {record["id"]: record for record in records}
    records = [by_id[reference_id] for reference_id in order]
    for index, record in enumerate(records, start=1):
        record["reference_number"] = str(index)
        record["vancouver"] = vancouver(record)
    fields = [
        "reference_number",
        "id",
        "authors",
        "title",
        "journal",
        "year",
        "volume",
        "issue",
        "pages",
        "doi",
        "pmid",
        "url",
        "claim",
        "verification_status",
        "vancouver",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    JSON_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    make_ledger()
    print(
        f"Wrote {len(records)} verified references and "
        f"{len(PUBLIC_SOURCES) + len(DOI_REFERENCES)} source-ledger entries."
    )


if __name__ == "__main__":
    main()
