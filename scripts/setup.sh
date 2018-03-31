#!/bin/bash -e
set -o pipefail

PARENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

if [ ! -d "$PARENT_DIR/virtualenv" ]; then
  echo 'Creating virtualenv...'
  virtualenv "$PARENT_DIR/virtualenv"
  echo 'Created virtualenv.'
fi

. "$PARENT_DIR/virtualenv/bin/activate"

echo 'Installing requirements...'
pip install -r "$PARENT_DIR/requirements.txt"
echo 'Installed requirements.'

echo 'Initializing database...'
./manage.py migrate
echo 'Initialized database.'

echo 'Loading data...'
./manage.py loaddata fixtures/initial_data.json
echo 'Loaded data.'
