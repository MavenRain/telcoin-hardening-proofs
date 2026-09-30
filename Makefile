.PHONY: bootstrap check inventory qualify gate-regression dispositions disposition-regression

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

qualify:
	python3 -I tools/check.py --require-complete

gate-regression:
	python3 -I tools/check_gate.py
