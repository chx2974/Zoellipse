# Self-contained: a local virtualenv in .venv/, created on first use from
# requirements-dev.txt (Python 3.10+ as `python3`, or set PYTHON=...).
PYTHON ?= python3
PY := .venv/bin/python
# Stamp file: requirements installed in .venv/.
VENV := .venv/.installed
export PYTHONPATH := src
# Serialise builds when several processes run at once: a whole target runs under one lock
# (lockf on macOS/BSD, flock on Linux, no lock if neither exists).
LOCK := $(shell command -v lockf >/dev/null 2>&1 && echo "lockf -k .build.lock" || \
          (command -v flock >/dev/null 2>&1 && echo "flock .build.lock"))

.PHONY: venv build check all clean serve sources release gfbuild _build _check

# Create / update the virtualenv when the requirements change.
$(VENV): requirements.txt requirements-dev.txt
	test -x $(PY) || $(PYTHON) -m venv .venv
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements-dev.txt
	touch $(VENV)

venv: $(VENV)

build: $(VENV)
	$(LOCK) $(MAKE) --no-print-directory _build

check: $(VENV)
	$(LOCK) $(MAKE) --no-print-directory _check

all: $(VENV)
	$(LOCK) $(MAKE) --no-print-directory _build _check

release: $(VENV)
	$(MAKE) --no-print-directory build
	$(MAKE) --no-print-directory check
	$(PY) scripts/release.py

# Rebuild from sources/ with Google Fonts' builder (as their CI does), in build/gf/.
gfbuild: $(VENV)
	rm -rf build/gf && mkdir -p build/gf && cp -R sources build/gf/sources
	cd build/gf/sources && PATH="$(abspath $(dir $(PY))):$$PATH" gftools builder config.yaml </dev/null
	@ls build/gf/fonts/variable

# Writes sources/*.ufo + *.designspace (also done by every build).
sources: $(VENV)
	$(LOCK) $(PY) -m zoellipse.build sources

_build:
	$(PY) -m zoellipse.build

_check:
	$(PY) scripts/check_tabular.py
	$(PY) scripts/check_outlines.py
	$(PY) scripts/check_squircle.py

clean:
	rm -rf build fonts/variable

serve: $(VENV)
	@echo "Specimen: http://localhost:8002/specimen/"
	$(PY) -m http.server 8002

.PHONY: qa
# Both Font Bakery profiles (reports in qa/). Non-zero exit (FAILs) does not stop make; read the reports.
qa: $(VENV)
	-$(PY) -m fontbakery check-universal --skip-network --ghmarkdown qa/fontbakery-universal.md "fonts/variable/Zoellipse[wght].ttf" "fonts/variable/Zoellipse-Italic[wght].ttf" </dev/null
	-$(PY) -m fontbakery check-googlefonts --skip-network --ghmarkdown qa/fontbakery-googlefonts.md "fonts/variable/Zoellipse[wght].ttf" "fonts/variable/Zoellipse-Italic[wght].ttf" </dev/null
