# Kritikus Tömeg

This project aims to rewrite Kritikus Tömeg from scratch. Readable code + open source = community driven development (hopefully).


## Developer guide

If you want to participate, here are some rules and guide.

Even though KT is Hungarian, code (especially open source code) should always be English. Someday, somewhere (maybe) some Danish guys might decide to start *Kritisk masse* (or the Russians *Критическая масса*). If code is English, they only need to translate URLs and templates (and build a database) (and of course raise a community).

For Hungarian communication and coordination use [this topic](http://kritikustomeg.org/forum.php?tid=187) on KT.

### TODO

See TODO.md

### Coding style

Most importantly:

- use only space for indentation (4 of them per level)
- lines should end with `LF` (`\n`, `\x0A`)
- everything (code, templates, database) is unicode, `utf-8` (collation: `utf8_hungarian_ci`)

Otherwise follow PEP-8 and use pylint.

### Install guide

See below.

### Database changes

Whenever you change `models.py`, don't forget to

- create a migration: `python manage.py schemamigration ktapp --auto`
- and apply it: `python manage.py migrate ktapp`

This way, not only your database schema will follow the change, but others can easily follow.

For more details [read this tutorial](http://south.readthedocs.org/en/latest/tutorial/part1.html).



## Install guide

### Python 2.7

Important: Python 3 *is* different.

### Virtualenv

Install [virtualenv](http://www.virtualenv.org/en/latest/).

Create a virtualenv in `kt`:

    cd /path/to/kt/
    virtualenv venv

Activate it:

`. venv/bin/activate`

Install all requirements:

`pip install -r requirements.txt`

### MySQL

Install [MySQL](http://dev.mysql.com/downloads/mysql/).

Create a database:

`create database ktdb default character set utf8 default collate utf8_hungarian_ci;`

And an admin user that Django uses (locally):

    grant all on ktdb.* to ktadmin@localhost identified by '<something>';
    flush privileges;

where `<something>` = anything random, but same as `kt/settings_local.py/DATABASE_DEFAULT_PASSWORD`.

Initialize your database (mostly empty tables):

    python manage.py syncdb
    python manage.py migrate

### Webserver

For development Django's built-in server is fine:

`python manage.py runserver [<port>]`

For production: use Apache, Lighttpd, nginx...

### kt/settings_local.py

This file is not in the public repo, because it contains secrets:

    DATABASE_DEFAULT_PASSWORD = ''
    SECRET_KEY = ''

Don't forget to create this file and fill in the secrets with some random stuff.
