.PHONY: help deps-system deps-venv test ci all

help:
	@echo "Available targets:"
	@echo "  deps-system  - Install system packages required for optional tests (Ubuntu/Debian)"
	@echo "  deps-venv    - Install Python dependencies into .venv (incl. test extras)"
	@echo "  test         - Run pytest inside .venv"
	@echo "  ci           - deps-venv + test (no system packages)"
	@echo "  all          - deps-system + deps-venv + test"

# Install system dependencies needed for optional filters/tests
# Requires sudo and apt on Debian/Ubuntu (e.g., WSL/Ubuntu).
deps-system:
	sudo apt-get update -y
	sudo apt-get install -y \
		poppler-utils libpoppler-cpp-dev \
		tesseract-ocr tesseract-ocr-eng \
		build-essential pkg-config python3-dev

# Install Python deps into the existing .venv
deps-venv:
	. .venv/bin/activate && pip install -r requirements.txt pytest pycodestyle docutils jq pytesseract pillow pdftotext apprise --disable-pip-version-check --no-input

test:
	. .venv/bin/activate && pytest -q

ci: deps-venv test

all: deps-system deps-venv test


