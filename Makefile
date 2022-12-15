test:
	poetry run pytest src

lint:
	poetry run black --line-length=200 src
	poetry run isort src
flake8:
	poetry run flake8 --max-line-length=200 --exclude=*/migrations src

migrations:
	poetry run python src/manage.py makemigrations

migrate:
	poetry run python src/manage.py migrate