.PHONY: lint lint-fix

lint:
	ruff check

lint-fix:
	ruff check --fix
