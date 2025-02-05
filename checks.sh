#!/bin/bash
set -eu
python -m mypy app
python -m ruff format app
python -m ruff check --fix --unsafe-fixes app
