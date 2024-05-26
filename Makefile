RUNNING_CONTAINER := $(shell docker compose ps --services --filter "status=running" | grep django )

test:
	@if [[ -n "${RUNNING_CONTAINER}" ]]; then \
		docker compose exec django poetry run pytest src/core src/users; \
	else \
		docker compose run --rm django poetry run pytest src/core src/users;\
	fi

test-ui:
	poetry run pytest src/tests

lint:
	poetry run black --line-length=200 src
	poetry run isort src
flake8:
	poetry run flake8 --max-line-length=200 --exclude=*/migrations src

migrations:
	poetry run python src/manage.py makemigrations

migrate:
	poetry run python src/manage.py migrate

gen:
	poetry run playwright codegen -b chromium --target python-pytest localhost:8000

translate_es:
	poetry run inv i18n -l es_ES
