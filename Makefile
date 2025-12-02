VENV_PATH = .venv
PYTHON = $(VENV_PATH)/bin/python
PIP = $(VENV_PATH)/bin/pip
PYTEST = $(VENV_PATH)/bin/pytest
RUFF = $(VENV_PATH)/bin/ruff
ALEMBIC = $(VENV_PATH)/bin/alembic
UVICORN = $(VENV_PATH)/bin/uvicorn
ALEMBIC_INI = services/migrant/app/alembic.ini

# ----------------------------TESTS----------------------------
test:
	$(PYTEST) -s -v
test-output:
	$(PYTEST) -s -v >output.log

# ----------------------------LINTERS----------------------------
ruff-check:
	$(RUFF) check
ruff-fix:
	$(RUFF) check --fix
ruff-format:
	$(RUFF) format
ruff-format-check:
	$(RUFF) format --check

# ----------------------------RUN APPS----------------------------
run-api:
	$(UVICORN) services.api.app.main:app --reload --host 0.0.0.0 --port 8001
run-cron:
	$(PYTHON) services/cron/app/main.py
run-events:
	$(PYTHON) services/events/app/main.py
run-rest:
	$(PYTHON) services/rest/app/manage.py runserver 8001

# ----------------------------MIGRATIONS----------------------------
# create migration with message
make-migrations:
	@echo "Enter migration message:"
	@read -p "Message: " msg; \
	$(ALEMBIC) -c $(ALEMBIC_INI) revision --autogenerate -m "$$msg"

# alternative migration through the service
migrate-service:
	$(PYTHON) services/migrant/app/main.py

# migrate using alembic - directly
migrate-alembic:
	$(ALEMBIC) -c $(ALEMBIC_INI) upgrade head

# ----------------------------INSTALL REQUIREMENTS----------------------------
install-all:
	$(PIP) install -r lib/requirements-dev.txt
	$(PIP) install -r services/api/requirements.txt
	$(PIP) install -r services/cron/requirements.txt
	$(PIP) install -r services/events/requirements.txt
	$(PIP) install -r services/migrant/requirements.txt
	$(PIP) install -r services/rest/requirements.txt
