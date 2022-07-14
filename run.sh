#!/bin/bash
poetry show
poetry run inv i18n --compile docs run -p -g
