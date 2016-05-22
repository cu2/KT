#!/bin/bash -e

if [[ $# -lt 1 ]]; then
  BUILD_CSS=1
  BUILD_JS=1
else
  if [[ "$1" == "js" ]]; then
    BUILD_CSS=0
    BUILD_JS=1
  elif [[ "$1" == "css" ]]; then
    BUILD_CSS=1
    BUILD_JS=0
  else
    echo "Usage: $0 [js|css]"
    exit 1
  fi
fi

if [[ $BUILD_CSS -eq 1 ]]; then
  echo '# BUILDING CSS...'
  cd bootstrap
  grunt dist
  cd ..
  cp bootstrap/dist/css/bootstrap.min.css ktapp/static/ktapp/css/kt-bootstrap.min.css
  csshash=$(md5 -q ktapp/static/ktapp/css/kt-bootstrap.min.css)
  gsed -i 's/\?csshash\=[^"]*"/\?csshash\='$csshash'"/g' ktapp/templates/ktapp/layout.html
  echo '# CSS BUILT.'
fi

if [[ $BUILD_JS -eq 1 ]]; then
  echo '# BUILDING JS...'
  jshash=$(md5 -q ktapp/static/ktapp/js/kt.js)
  gsed -i 's/\?jshash\=[^"]*"/\?jshash\='$jshash'"/g' ktapp/templates/ktapp/layout.html
  echo '# JS BUILT.'
fi
