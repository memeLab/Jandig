RUNNING_CONTAINER := $(shell docker compose ps --services --filter "status=running" | grep django )

test:
	@if [[ -n "${RUNNING_CONTAINER}" ]]; then \
		docker compose exec django uv run pytest src/core src/users src/blog; \
	else \
		docker compose run --rm django uv run pytest src/core src/users src/blog;\
	fi

test-ui:
	docker compose up -d
	uv run pytest src/tests

lint:
	uv run ruff format src
	uv run ruff check --fix src

check: 
	uv run ruff check

migrations:
	uv run python src/manage.py makemigrations

migrate:
	uv run python src/manage.py migrate

gen:
	uv run playwright codegen -b chromium --target python-pytest localhost:8000

translate_es:
	docker compose exec django uv run inv i18n -l es_ES

translate_pt:
	docker compose exec django uv run inv i18n -l pt_BR