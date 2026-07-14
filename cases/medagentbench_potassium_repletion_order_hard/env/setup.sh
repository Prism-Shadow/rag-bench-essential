#!/usr/bin/env bash
set -euo pipefail

IMAGE="${MEDAGENTBENCH_IMAGE:-medagentbench}"
UPSTREAM="${MEDAGENTBENCH_UPSTREAM_IMAGE:-jyxsu6/medagentbench:latest}"
CONTAINER="${MEDAGENTBENCH_CONTAINER:-agenticrag-medagentbench}"
PORT="${MEDAGENTBENCH_PORT:-8080}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required for live MedAgentBench mode" >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "docker daemon is not running" >&2
  exit 1
fi

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker pull "$UPSTREAM"
  docker tag "$UPSTREAM" "$IMAGE"
fi

if docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "MedAgentBench container already running: $CONTAINER"
else
  if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    docker start "$CONTAINER" >/dev/null
  else
    docker run -d --name "$CONTAINER" -p "127.0.0.1:$PORT:8080" "$IMAGE" >/dev/null
  fi
fi

echo "FHIR_API_BASE=http://localhost:${PORT}/fhir/"
