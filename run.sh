#!/bin/bash
poetry show
poetry run inv collect db -p i18n --compile docs run -p -g
