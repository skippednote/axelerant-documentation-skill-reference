PYTHON ?= python3
AUDIT := skills/axelerant-engineering-documentation/scripts/docs_audit.py
.PHONY: audit test sample plugin-check workflow-check coverage verify verify-release
audit:
	$(PYTHON) $(AUDIT) . --strict
	$(PYTHON) $(AUDIT) sample/dispatch --strict
test:
	$(PYTHON) -m unittest discover -s tests -v
sample:
	$(MAKE) -C sample/dispatch verify
plugin-check:
	$(PYTHON) scripts/validate_plugin.py
workflow-check:
	$(PYTHON) scripts/check_workflows.py
coverage:
	$(PYTHON) scripts/check_contract_coverage.py
verify: audit test sample plugin-check workflow-check coverage
verify-release: verify
	$(PYTHON) scripts/verify_release.py
