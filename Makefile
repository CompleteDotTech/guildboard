.PHONY: planning-check planning-audit
planning-check:
	python3 scripts/github-bootstrap/validate.py
planning-audit:
	python3 scripts/github-bootstrap/audit.py
