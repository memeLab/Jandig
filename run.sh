#!/bin/bash
poetry show
poetry run inv db -p i18n --compile docs run -p -g
