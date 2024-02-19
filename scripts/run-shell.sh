#!/usr/bin/env bash
set -euo pipefail

__root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"

DC_FILE="${__root_dir}/docker/dev/docker-compose.yml"
PROJECT_NAME="kt-dev"

function dc {
  docker compose -f "${DC_FILE}" -p "${PROJECT_NAME}" "$@"
}

KT_CONTAINER_ID=$(dc ps -q kt)

if [[ -z "${KT_CONTAINER_ID}" ]]; then
  echo 'Error: dev env is not running.'
  echo 'Please run:'
  echo './scripts/start-dev.sh'
  exit 1
fi

exec docker exec -it "${KT_CONTAINER_ID}" python2 manage.py shell
