# Kritikus Tömeg

This project aims to rewrite Kritikus Tömeg from scratch. Readable code + open source = community driven development (hopefully).

## Developer guide

### TODO

See TODO.md

### Coding style

Most importantly:

- use only space for indentation (4 of them per level)
- lines should end with `LF` (`\n`, `\x0A`)
- everything (code, templates, database) is unicode, utf-8 (collation: utf8_hungarian_ci)

Otherwise follow PEP-8 and use pylint.

### Install guide

#### Python 2.7

#### Django 1.5.4

Linux, Mac OS X: `sudo pip install Django==1.5.4`

Windows: `pip install Django` (how to specify version?)

(Get `pip` from [here](http://www.pip-installer.org/en/latest/))

#### South

#### MySQL

`create database ktdb default character set utf8 default collate utf8_hungarian_ci;`

`grant all on ktdb.* to ktadmin@localhost identified by '';` (anything random, but same as kt/settings_local.py/DATABASES/default/PASSWORD)

`flush privileges;`

#### Webserver

For development: Django

`python manage.py runserver`

For production: Apache, Lighttpd, nginx...

#### `kt/settings_local.py`

This file is not in the public repo, because it contains secrets:

`DATABASE_DEFAULT_PASSWORD = ''`

`SECRET_KEY = ''`

Don't forget to create this file and fill in the secrets with some random stuff.
