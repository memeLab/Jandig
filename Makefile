test:
	poetry run pytest src

lint:
	poetry run black src
	poetry run isort src

migrations:
	poetry run python src/manage.py makemigrations

migrate:
	poetry run python src/manage.py migrate