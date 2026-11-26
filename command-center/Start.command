#!/bin/bash
set -eu
cd "$(dirname "$0")"
umask 077
export CENTER_DATA="${CENTER_DATA:-$HOME/.sahab-center}"
mkdir -p "$CENTER_DATA"
if [ ! -x "$CENTER_DATA/venv/bin/python" ]; then python3 -m venv "$CENTER_DATA/venv"; fi
py="$CENTER_DATA/venv/bin/python"
"$py" -m pip install --disable-pip-version-check -q -r runtime/requirements.txt
"$py" -m runtime.setup
if [ -z "${OPENAI_API_KEY:-}" ]; then
  read -rs -p 'OpenAI API key (press Return for vault only): ' OPENAI_API_KEY
  echo
  export OPENAI_API_KEY
fi
echo 'http://127.0.0.1:8765'
exec "$py" -m uvicorn runtime.server:app --host 127.0.0.1 --port 8765
