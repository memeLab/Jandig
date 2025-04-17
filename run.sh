#!/bin/bash

USE_GUNICORN=${USE_GUNICORN:-true}
# Convert variables to lowercase for case-insensitive comparison
USE_GUNICORN=$(echo "$USE_GUNICORN" | tr '[:upper:]' '[:lower:]')



uv pip list
uv run python src/manage.py collectstatic --no-input
uv run python src/manage.py migrate
uv run sphinx-build docs/ build/
uv run python src/manage.py compilemessages --ignore .venv --ignore cache

if [ "$USE_GUNICORN" = "true" ]; then
  echo "Running Gunicorn Server"
  bash -c "cd src && uv run gunicorn --reload --worker-connections=10000 --workers=4 --log-level debug --bind 0.0.0.0:8000 config.wsgi"
else
  echo "Running Django development server"
  uv run python src/manage.py runserver 0.0.0.0:8000
fi