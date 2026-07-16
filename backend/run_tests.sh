#!/usr/bin/env bash
# run_tests.sh — Run the Soccer Solver test suite
#
# Usage:
#   bash run_tests.sh           — run all tests
#   bash run_tests.sh -v        — verbose output
#   bash run_tests.sh -k transition  — run only transition tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -f "$VENV_DIR/bin/pytest" ]; then
  echo "❌  pytest not found. Run: bash setup.sh"
  exit 1
fi

echo "🧪  Running Soccer Solver tests..."
echo ""

cd "$SCRIPT_DIR"
"$VENV_DIR/bin/pytest" app/soccer/tests/ -v "$@"
