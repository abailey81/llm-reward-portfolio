# llm-reward-portfolio — developer entry points.
# The deterministic core (inference, measurement, sandbox, baselines, env) runs on a light
# scientific stack; the agent-training / LLM paths additionally need torch + SB3 + an API key.

PY ?= python
VENV ?= .venv
VPY := $(VENV)/bin/python

.DEFAULT_GOAL := help
.PHONY: help venv install install-dev test test-fast lint format typecheck \
        smoke freeze power campaign analyze clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	 awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

venv:  ## Create a venv that inherits system scientific libs + adds gymnasium
	$(PY) -m venv $(VENV) --system-site-packages
	$(VPY) -m pip install -U pip
	$(VPY) -m pip install gymnasium pytest pytest-cov ruff mypy

install:  ## Install the package (full deps incl. torch/SB3 — for training)
	$(VPY) -m pip install -e .

install-dev:  ## Install with dev extras
	$(VPY) -m pip install -e ".[dev]"

test:  ## Run the full test suite
	$(VPY) -m pytest

test-fast:  ## Run tests, skipping agent-training ('slow') tests
	$(VPY) -m pytest -m "not slow"

lint:  ## Ruff lint
	$(VPY) -m ruff check src tests scripts

format:  ## Ruff format
	$(VPY) -m ruff format src tests scripts

typecheck:  ## mypy
	$(VPY) -m mypy src

smoke:  ## Phase 0 gate — SB3 SAC + TQC on the RTX 4090, online, timed
	$(VPY) scripts/smoke_test.py

power:  ## Phase 1.C — power analysis
	$(VPY) scripts/power_analysis.py

freeze:  ## Phase 1.E — hash + freeze the pre-registration
	$(VPY) scripts/freeze.py

campaign:  ## Phase 3 — run the campaign (config/campaign.yaml)
	$(VPY) scripts/run_campaign.py

analyze:  ## Phase 4 — hypothesis tests + tables
	$(VPY) scripts/analyze_results.py

clean:  ## Remove caches and build artifacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info
