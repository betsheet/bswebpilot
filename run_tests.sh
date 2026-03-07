#!/usr/bin/env zsh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [[ ! -f "$PYTHON" ]]; then
    echo "ERROR: no se encontró el entorno virtual en .venv/"
    echo "Crea el venv y ejecuta: pip install -e .[dev]"
    exit 1
fi

echo "========================================"
echo "  bswebpilot · suite de tests"
echo "========================================"
echo ""

"$PYTHON" -m pytest tests/ -v "$@"

