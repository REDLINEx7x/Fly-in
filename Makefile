PYTHON = python3
MAIN = fly-in.py
MAP ?= map.txt

install:
	@pip install -r requirements.txt

run:
	@$(PYTHON) $(MAIN) $(MAP) || true

debug:
	@$(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete

lint:
	@$(PYTHON) -m flake8 *.py --extend-ignore=E501 || true
	@$(PYTHON) -m mypy *.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs || true

.PHONY: install run debug clean lint
