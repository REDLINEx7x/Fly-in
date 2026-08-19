PYTHON = python3
FILE ?= map.txt

install:
	pip install pydantic flake8 mypy pygame

run:
	$(PYTHON) fly-in.py $(FILE)

visual:
	$(PYTHON) fly-in.py --visual $(FILE)

debug:
	$(PYTHON) -m pdb fly-in.py $(FILE)

clean:
	rm -rf __pycache__ .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run visual debug clean lint lint-strict
