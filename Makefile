PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: all environment clean-generated

all: environment
	$(PYTHON) scripts/sample_size_analysis.py
	$(PYTHON) scripts/mock_analysis.py
	$(PYTHON) scripts/verify_references.py
	$(PYTHON) scripts/generate_protocol_package.py
	$(PYTHON) scripts/qc_package.py

environment: $(PYTHON)

$(PYTHON): reproducibility/requirements.txt
	python3 -m venv .venv
	$(PIP) install --requirement reproducibility/requirements.txt

clean-generated:
	@echo "Generated outputs are intentionally retained; remove only in a disposable checkout."
