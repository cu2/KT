#!/bin/bash -e

echo '# BUILDING CSS...'
cd bootstrap
grunt dist
cd ..
cp bootstrap/dist/css/bootstrap.min.css ktapp/static/ktapp/css/kt-bootstrap.min.css
echo '# CSS BUILT.'

csshash=$(md5 -q ktapp/static/ktapp/css/kt-bootstrap.min.css)
gsed -i 's/\?csshash\=[^"]*"/\?csshash\='$csshash'"/g' ktapp/templates/ktapp/layout.html

jshash=$(md5 -q ktapp/static/ktapp/js/kt.js)
gsed -i 's/\?jshash\=[^"]*"/\?jshash\='$jshash'"/g' ktapp/templates/ktapp/layout.html

echo '# DONE DONE.'
