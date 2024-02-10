#!/usr/bin/env bash
set -euo pipefail

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"

DC_FILE="${__root_dir}/docker/dev/docker-compose.yml"
PROJECT_NAME="kt-dev"

function dc {
  docker compose -f "${DC_FILE}" -p "${PROJECT_NAME}" "$@"
}

function stop_system {
  dc down
}
trap stop_system EXIT


stop_system
dc up -d
KT_CONTAINER_ID=$(dc ps -q kt)

echo 'Dumping test data...'
docker exec "${KT_CONTAINER_ID}" python2 manage.py dumpdata --indent=4 ktapp > fixtures/initial_data.json
echo 'Dumped.'

# NOTE: trap is doing "dc down"
