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

echo 'Initializing database...'
docker volume rm -f kt-db
docker volume create kt-db
dc up -d
DB_CONTAINER_ID=$(dc ps -q db)
KT_CONTAINER_ID=$(dc ps -q kt)
docker exec -i "${DB_CONTAINER_ID}" mysql -u root < "${__dir}/create-dev-db.sql"
docker exec "${KT_CONTAINER_ID}" python2 manage.py migrate
echo 'Initialized.'

echo 'Loading test data...'
docker exec "${KT_CONTAINER_ID}" python2 manage.py loaddata fixtures/initial_data.json
echo 'Loaded.'

# NOTE: trap is doing "dc down"
