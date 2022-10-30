test:
	poetry run python src/manage.py test

lint:
	poetry run black
	poetry run isort

migrations:
	poetry run python src/manage.py makemigrations

migrate:
	poetry run python src/manage.py migrate