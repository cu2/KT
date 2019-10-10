#!/usr/bin/env bash
set -euo pipefail

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


echo "########## Building dev image..."
"${__dir}/build-dev-image.sh"
echo "########## Built."

echo "########## Initializing dev db..."
"${__dir}/init-dev-db.sh"
echo "########## Initialized."
