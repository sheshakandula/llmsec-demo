#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate llmsec-312 >/dev/null
python -m uvicorn api.main:app --reload