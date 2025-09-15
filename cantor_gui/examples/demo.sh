#!/usr/bin/env bash
set -euo pipefail

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

python -m cantor_gui --mode line --depth 6 --bg '#ffffff' --fg '#1b1f23'
