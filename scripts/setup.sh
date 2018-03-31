#!/bin/bash -e
set -o pipefail

PARENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

if [ ! -d "$PARENT_DIR/virtualenv" ]; then
  virtualenv "$PARENT_DIR/virtualenv"
fi

. "$PARENT_DIR/virtualenv/bin/activate"

pip install -r "$PARENT_DIR/requirements.txt"

./manage.py migrate
./manage.py loaddata fixtures/initial_data.json
