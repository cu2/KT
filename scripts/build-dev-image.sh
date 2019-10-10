#!/usr/bin/env bash
set -euo pipefail

__root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"


docker build -t kt-dev:0.0 -f "${__root_dir}/docker/dev/Dockerfile" "${__root_dir}"
