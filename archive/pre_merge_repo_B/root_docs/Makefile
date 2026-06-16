.PHONY: setup lock test lint smoke pull-pilot reconcile freeze-design \
        data-probe data-pull data-build data-validate data-reconcile data-eda data-status \
        pull-universe

setup:
	pip install -r requirements.txt

lock:
	pip freeze > requirements.lock && echo "requirements.lock written — commit it (ADR-002)."

test:
	python -m pytest

lint:
	ruff check src tests

smoke:
	python -m src.smoke_iqn_sac

pull-pilot:
	python -m src.pull_pilot

reconcile:
	python -m src.reconcile

freeze-design:
	@git log -1 --format='Freeze hash: %H (%ad)' -- PREREGISTRATION.md || echo "Commit PREREGISTRATION.md first."

# --- data platform (src/data; ADR-012) ---
data-probe:
	python -m src.data.cli probe

data-pull:
	python -m src.data.cli pull --pilot

data-build:
	python -m src.data.cli build

data-validate:
	python -m src.data.cli validate

data-reconcile:
	python -m src.data.cli reconcile

data-eda:
	python -m src.data.cli eda

data-status:
	python -m src.data.cli status

# A1-A5 universe acquisition (ADR-019). Dry-run by default (plan only, no session);
# the day entitlement lands, run `make pull-universe LIVE=1` for the live entitled pull.
pull-universe:
	python -m src.data.cli pull-universe $(if $(LIVE),--live,)

# Assemble the entitled pulls into the PIT research panel (gold suffix _univ; ADR-021)
build-universe:
	python -m src.data.cli build-universe
