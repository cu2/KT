#!/bin/bash -e
set -o pipefail

PARENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

. "$PARENT_DIR/virtualenv/bin/activate"

./manage.py runserver
