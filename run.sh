#!/bin/bash
poetry install
poetry show
# poetry run python src/manage.py collectstatic --no-input
poetry run python src/manage.py migrate
poetry run sphinx-build docs/ build/
poetry run python etc/scripts/compilemessages.py

bash -c "cd src && poetry run gunicorn --reload --worker-connections=10000 --workers=4 --log-level debug --bind 0.0.0.0:8000 config.wsgi"
# poetry run python src/manage.py runserver 0.0.0.0:8000