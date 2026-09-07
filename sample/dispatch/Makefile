PYTHON ?= python3
export PYTHONPATH := $(CURDIR)/src
.PHONY: up init run worker worker-once send status test smoke lint docs-check verify book book-pdf package clean
up init:
	$(PYTHON) -m dispatch init
run:
	$(PYTHON) -m dispatch api
worker:
	$(PYTHON) -m dispatch worker
worker-once:
	$(PYTHON) -m dispatch worker-once
send:
	$(PYTHON) -m dispatch send
status:
	$(PYTHON) -m dispatch status
test:
	$(PYTHON) -m unittest discover -s tests -v
smoke:
	$(PYTHON) -m unittest discover -s tests -p 'test_dispatch.py' -k http_roundtrip -v
lint:
	$(PYTHON) -c "import ast,pathlib; [ast.parse(p.read_text()) for d in ('src','tests','scripts') for p in pathlib.Path(d).rglob('*.py')]; print('Python syntax: OK')"
docs-check:
	$(PYTHON) ../../skills/axelerant-engineering-documentation/scripts/docs_audit.py . --strict
verify: lint test docs-check
book:
	$(PYTHON) ../../scripts/build_book.py . --title dispatch
book-pdf:
	$(PYTHON) ../../scripts/build_book.py . --title dispatch --pdf
package:
	$(PYTHON) scripts/package_example.py
clean:
	rm -rf .state dist
