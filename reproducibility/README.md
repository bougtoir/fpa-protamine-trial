
# Reproducibility

All validation data are synthetic and are not clinical observations.

## Environment

Python dependencies are pinned in `requirements.txt`. From the project root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r reproducibility/requirements.txt
.venv/bin/python scripts/verify_references.py
.venv/bin/python scripts/sample_size_analysis.py
.venv/bin/python scripts/mock_analysis.py
.venv/bin/python scripts/generate_protocol_package.py
.venv/bin/python scripts/qc_package.py
```

## Provenance

- Trial constants: `config/trial_design.json`
- Sample-size source: `scripts/sample_size_analysis.py`
- Calculated constants: `output/analysis_constants.json`
- Synthetic validation: `scripts/mock_analysis.py`
- Documents: `scripts/generate_protocol_package.py`
- QC: `scripts/qc_package.py`

The synthetic primary model converged: True. This is a software-path check, not an efficacy result.
