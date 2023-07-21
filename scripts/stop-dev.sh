#!/usr/bin/env bash
set -euo pipefail

__root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"


docker compose \
  -f "${__root_dir}/docker/dev/docker-compose.yml" \
  -p kt-dev \
  down
