PYTHON  = python3
MAIN    = fly-in.py
MAP    ?= map.txt

all: run

install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

run:
	@$(PYTHON) $(MAIN) $(MAP) || true

debug:
	@$(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	@echo "Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete

fclean: clean

re: fclean all

lint:
	@echo "Running Flake8..."
	@$(PYTHON) -m flake8 . --extend-ignore=E501 || true
	@echo "🧪 Running Mypy..."
	@$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs || true

.PHONY: all install run debug clean fclean re lint
