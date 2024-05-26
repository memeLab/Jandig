#!/bin/bash
poetry show
poetry run inv collect db i18n --compile docs run -g
