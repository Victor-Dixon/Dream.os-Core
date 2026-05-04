#!/usr/bin/env bash
set -euo pipefail

tree -L "${1:-3}" \
  -I '__pycache__|*.pyc|*.pyo|.pytest_cache|.git|*.zip|tree_noise_prune_*.json|finalize_tree_cleanup_*.json'
