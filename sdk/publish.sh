#!/usr/bin/env bash
# Publish freeproxydb SDK to PyPI (or TestPyPI).
#
# Usage:
#   ./publish.sh              # build + upload to PyPI
#   ./publish.sh --test       # upload to TestPyPI
#   ./publish.sh --dry-run    # build only, no upload
#   ./publish.sh --yes        # skip confirmation
#
# Credentials (pick one):
#   export TWINE_USERNAME=__token__
#   export TWINE_PASSWORD=pypi-AgEI...
#   or ~/.pypirc

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TEST=0
DRY_RUN=0
YES=0

for arg in "$@"; do
  case "$arg" in
    --test) TEST=1 ;;
    --dry-run) DRY_RUN=1 ;;
    --yes|-y) YES=1 ;;
    -h|--help)
      sed -n '2,14p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
  esac
done

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
  echo "Error: python not found" >&2
  exit 1
fi

PYTHON=python3
command -v python3 >/dev/null 2>&1 || PYTHON=python

VERSION="$("$PYTHON" -c "import pathlib,re; t=pathlib.Path('pyproject.toml').read_text(encoding='utf-8'); m=re.search(r'^version\s*=\s*\"([^\"]+)\"', t, re.M); print(m.group(1) if m else '?')")"
REPO="PyPI"
REPO_URL="https://upload.pypi.org/legacy/"
if [[ "$TEST" -eq 1 ]]; then
  REPO="TestPyPI"
  REPO_URL="https://test.pypi.org/legacy/"
fi

echo "========================================"
echo " freeproxydb SDK publish"
echo " version : $VERSION"
echo " target  : $REPO"
echo " dir     : $SCRIPT_DIR"
echo "========================================"

if [[ "$YES" -ne 1 ]]; then
  read -r -p "Continue? [y/N] " ans
  case "${ans,,}" in
    y|yes) ;;
    *) echo "Cancelled."; exit 0 ;;
  esac
fi

echo "[1/4] Installing build tools..."
"$PYTHON" -m pip install -U pip build twine >/dev/null

echo "[2/4] Cleaning old artifacts..."
rm -rf dist build *.egg-info freeproxydb/*.egg-info 2>/dev/null || true

echo "[3/4] Building sdist + wheel..."
"$PYTHON" -m build

echo "Built artifacts:"
ls -la dist/

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run complete (upload skipped)."
  exit 0
fi

if [[ -z "${TWINE_USERNAME:-}" || -z "${TWINE_PASSWORD:-}" ]]; then
  if [[ ! -f "$HOME/.pypirc" ]]; then
    echo "Error: set TWINE_USERNAME and TWINE_PASSWORD, or configure ~/.pypirc" >&2
    exit 1
  fi
fi

echo "[4/4] Uploading to $REPO..."
"$PYTHON" -m twine upload --non-interactive --repository-url "$REPO_URL" dist/*

echo "Done. Install with:"
if [[ "$TEST" -eq 1 ]]; then
  echo "  pip install -i https://test.pypi.org/simple/ freeproxydb==$VERSION"
else
  echo "  pip install freeproxydb==$VERSION"
fi
