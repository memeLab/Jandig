RUNNING_CONTAINER := $(shell docker compose ps --services --filter "status=running" | grep django )

test:
	@if [[ -n "${RUNNING_CONTAINER}" ]]; then \
		docker compose exec django poetry run pytest src/core src/users src/blog; \
	else \
		docker compose run --rm django poetry run pytest src/core src/users src/blog;\
	fi

test-ui:
	docker compose up -d
	poetry run pytest src/tests

lint:
	poetry run ruff format src
	poetry run ruff check --fix src

check: 
	poetry run ruff check

migrations:
	poetry run python src/manage.py makemigrations

migrate:
	poetry run python src/manage.py migrate

gen:
	poetry run playwright codegen -b chromium --target python-pytest localhost:8000

translate_es:
	poetry run inv i18n -l es_ES

translate_pt:
	poetry run inv i18n -l pt_BR