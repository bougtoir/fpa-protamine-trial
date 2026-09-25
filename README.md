# IF-U-PLEASE II prospective trial protocol

Submission and reproducibility package for a planned multicentre, randomised, double-blind, placebo-controlled trial of flurbiprofen axetil before protamine in adult non-CABG on-pump cardiac surgery.

No participant has been enrolled and no prospective clinical result is reported. Files under `reproducibility/data/` are explicitly synthetic software-validation data.

## Rebuild

```bash
make all
```

This creates a local virtual environment, installs pinned dependencies, reruns sample-size and synthetic validation analyses, verifies saved reference metadata, regenerates all documents/figures, performs package QC, and rebuilds both ZIP archives.

## Principal outputs

- `ACA_FPA_protocol_submission_package.zip`
- `reproducibility_bundle.zip`
- `FINAL_HANDOFF.txt`
- `FINAL_QC_REPORT.md`

The retrospective source documents are private inputs and are intentionally excluded. Their extracted numeric audit, provenance limitations, and published citation are included. The locally held retrospective PDF was generated from the supplied DOCX and is not independently verified as the final publisher PDF.
