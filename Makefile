.PHONY: bootstrap check inventory qualify gate-regression

bootstrap:
	python3 -I tools/bootstrap.py

check:
	python3 -I tools/check.py

inventory:
	python3 -I tools/catalog.py

qualify:
	python3 -I tools/check.py --require-complete

gate-regression:
	python3 -I tools/check_gate.py
