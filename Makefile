.PHONY: bootstrap check inventory qualify gate-regression dispositions disposition-regression scope scope-regression audit audit-regression

bootstrap:
	python3 -I tools/bootstrap.py

check:
	python3 -I tools/check.py

inventory:
	python3 -I tools/catalog.py

dispositions:
	python3 -I tools/dispositions.py

disposition-regression:
	python3 -I tools/check_dispositions.py

scope:
	python3 -I tools/scope.py

scope-regression:
	python3 -I tools/check_scope.py

audit:
	python3 -I tools/audit.py

audit-regression:
	python3 -I tools/check_audit.py

qualify:
	python3 -I tools/check.py --require-complete

gate-regression:
	python3 -I tools/check_gate.py
