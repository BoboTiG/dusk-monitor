#!/bin/bash
set -eu
python -m ruff format app
python -m ruff check --fix --unsafe-fixes app
python -m mypy app
