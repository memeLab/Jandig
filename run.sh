#!/bin/bash

# Set default values for environment variables if not provided
INSTALL_DEV=${INSTALL_DEV:-false}
USE_GUNICORN=${USE_GUNICORN:-true}

# Convert variables to lowercase for case-insensitive comparison
INSTALL_DEV=$(echo "$INSTALL_DEV" | tr '[:upper:]' '[:lower:]')
USE_GUNICORN=$(echo "$USE_GUNICORN" | tr '[:upper:]' '[:lower:]')

uv sync --frozen --no-dev

if [ "$INSTALL_DEV" = "true" ]; then
  uv sync --frozen
fi

uv pip list
uv run python src/manage.py collectstatic --no-input
uv run python src/manage.py migrate
uv run sphinx-build docs/ build/
uv run python etc/scripts/compilemessages.py

if [ "$USE_GUNICORN" = "true" ]; then
  echo "Running Gunicorn Server"
  bash -c "cd src && uv run gunicorn --reload --worker-connections=10000 --workers=4 --log-level debug --bind 0.0.0.0:8000 config.wsgi"
else
  echo "Running Django development server"
  uv run python src/manage.py runserver 0.0.0.0:8000
fi