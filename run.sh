#!/bin/bash

USE_GRANIAN=${USE_GRANIAN:-true}
# Convert variables to lowercase for case-insensitive comparison
USE_GRANIAN=$(echo "$USE_GRANIAN" | tr '[:upper:]' '[:lower:]')

uv pip list
python src/manage.py collectstatic --no-input
python src/manage.py migrate
sphinx-build docs/ build/
python src/manage.py compilemessages --ignore .venv --ignore cache

if [ "$USE_GRANIAN" = "true" ]; then
  echo "Running Granian Server"
  bash -c "cd src && granian --interface asginl config.asgi:app --host 0.0.0.0 --port 8000 --workers 1 --reload"
else
  echo "Running Django development server"
  python src/manage.py runserver 0.0.0.0:8000
fi