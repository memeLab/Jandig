#!/bin/bash
pip list
inv db -p i18n --compile docs run -p -g
