#!/usr/bin/env bash
set -euo pipefail

__root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"

DC_FILE="${__root_dir}/docker/dev/docker-compose.yml"
PROJECT_NAME="kt-dev"

function dc {
  docker compose -f "${DC_FILE}" -p "${PROJECT_NAME}" "$@"
}

DB_CONTAINER_ID=$(dc ps -q db)

exec docker exec -it "${DB_CONTAINER_ID}" mysql -u ktadmin --password=password ktdb_dev
