PYTHON = python3
MAIN = main.py
VENV = venv
PIP = $(VENV)/bin/pip
PY = $(VENV)/bin/python

all: install

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy colorama

run:
	$(PY) $(MAIN) $(FILE)

debug:
	$(PY) -m pdb $(MAIN) $(FILE)

lint:
		flake8 .
		mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	rm -rf __pycache__ .mypy_cache $(VENV)
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

.PHONY: all install run debug lint lint-strict clean
