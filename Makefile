VENV_PATH = .venv
PYTHON = $(VENV_PATH)/bin/python
PIP = $(VENV_PATH)/bin/pip
PYTEST = $(VENV_PATH)/bin/pytest
RUFF = $(VENV_PATH)/bin/ruff
ALEMBIC = $(VENV_PATH)/bin/alembic
UVICORN = $(VENV_PATH)/bin/uvicorn
ALEMBIC_INI = services/migrant/app/alembic.ini

# ----------------------------TESTS----------------------------
# run all tests with output in terminal
test:
	$(PYTEST) -s -v
# run all tests with output in file output.log
test_output:
	$(PYTEST) -s -v >output.log


# ----------------------------RUN APPS----------------------------
# run API
run_api:
	$(UVICORN) services.api.app.main:app --reload --host 0.0.0.0 --port 8001
# run cron
run_cron:
	$(PYTHON) services/cron/app/main.py
# run events
run_events:
	$(PYTHON) services/events/app/main.py

# ----------------------------LINTERS----------------------------
# ruff check
ruff_check:
	$(RUFF) check

# ----------------------------MIGRATIONS----------------------------
# create migration with message
make_migrations:
	@echo "Enter migration message:"
	@read -p "Message: " msg; \
	$(ALEMBIC) -c $(ALEMBIC_INI) revision --autogenerate -m "$$msg"

# migrate using alembic - directly
migrate:
	$(ALEMBIC) -c $(ALEMBIC_INI) upgrade head

# alternative migration through the service
migrate_service:
	$(PYTHON) services/migrant/app/main.py
