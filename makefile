VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PACKAGE_DIR = moodle_to_vikwikiquiz

.PHONY: all venv install run

all: venv install run

venv:
	@python3 -m venv $(VENV)

install: venv
	@$(PIP) install -r requirements.txt

run: venv
	@$(PYTHON) -m $(PACKAGE_DIR).main $(ARGS)