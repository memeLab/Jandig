test:
	poetry run python src/manage.py test

lint:
	poetry run black
	poetry run isort