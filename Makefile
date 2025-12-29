.PHONY: setup run test lint format clean check context

# 🐍 Setup Environment
setup:
	python3 -m venv .venv
	@echo ">> Run: source .venv/bin/activate (Mac/Linux) or .venv\\Scripts\\activate (Win)"
	@echo ">> Then: pip install -e .[dev]"

# 🚀 Run Application
run:
	PYTHONPATH=. python src/interface/main.py

# 🧪 Run Tests
test:
	PYTHONPATH=. pytest tests -v

# 🧹 Lint & Type Check
lint:
	PYTHONPATH=. ruff check .
	PYTHONPATH=. mypy .

# ✨ Auto Format
format:
	ruff check --fix .
	ruff format .

# ✅ All Checks (CI/CD)
check: lint test

# 🗑️ Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf .venv

# 🤖 Dump Context for AI
context:
	python scripts/dump_context.py > project_context.txt
	@echo "Context dumped to project_context.txt"
