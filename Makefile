RUNNING_CONTAINER := $(shell docker compose ps --services --filter "status=running" | grep django )

test:
	@if [ -n "${RUNNING_CONTAINER}" ]; then \
		docker compose exec django pytest src/core src/users src/blog; \
	else \
		docker compose run --rm django pytest src/core src/users src/blog;\
	fi

test-ui:
	docker compose up -d
	docker compose exec django pytest src/ui_tests

test-all:
	docker compose up -d
	docker compose exec django pytest

lint:
	uv run ruff format src 
	uv run ruff check --extend-select I --fix src

check: 
	uv run ruff check

migrations:
	DJANGO_SECRET_KEY=change_me uv run python src/manage.py makemigrations

migrate:
	docker compose up -d
	docker compose exec django python src/manage.py migrate

collectstatic:
	docker compose up -d
	docker compose exec django python src/manage.py collectstatic --noinput

gen:
	uv run playwright codegen -b chromium --target python-pytest localhost:8000

translate_%:
	echo "Extracting Django strings..."
	DJANGO_SECRET_KEY=change_me uv run python3 ./src/manage.py makemessages --ignore .venv --ignore cache --keep-pot --locale $*
	
	echo "Extracting Jinja2 strings..."
	pybabel extract -F ./etc/babel.cfg -o ./locale/jinja2.pot .
	
	echo "Merging Django + Jinja2 strings..."
	msgcat ./locale/django.pot ./locale/jinja2.pot --use-first -o ./locale/join.pot
	
	echo "Removing unwanted language header..."
	sed -i '/"Language: \\n"/d' ./locale/join.pot
	
	echo "Merge translations into language..."
	msgmerge ./locale/$*/LC_MESSAGES/django.po ./locale/join.pot -U
	rm ./locale/*.pot

# Aliases for backward compatibility
translate_es: 
	@$(MAKE) translate_es_ES
translate_pt:
	@$(MAKE) translate_pt_BR
