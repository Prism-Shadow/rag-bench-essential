#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${MEDAGENTBENCH_CONTAINER:-agenticrag-medagentbench}"

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  if docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    docker stop "$CONTAINER" >/dev/null
    echo "stopped $CONTAINER"
  fi
fi
