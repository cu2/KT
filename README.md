# Kritikus Tömeg

[Kritikus Tömeg](https://kritikustomeg.org/) is a Hungarian movie site, community, database, recommendation engine.


## Developer guide

If you want to participate, here are some rules and guidelines.

Even though KT is Hungarian, code (especially open source code) should always be English. Someday, somewhere (maybe) some Danish guys might decide to start *Kritisk masse* (or the Russians *Критическая масса*). If code is English, they only need to translate URLs and templates (and build a database) (and of course raise a community).

For Hungarian communication and coordination use [this topic](https://kritikustomeg.org/forum/187/kritikus-kod) on KT.

Please use "standard" coding style:

- use only space for indentation (4 of them per level)
- lines should end with `LF` (`\n`, `\x0A`)
- everything (code, templates, database) is unicode, `utf-8` (collation: `utf8_hungarian_ci`)

Otherwise follow PEP-8 and use pylint.


## How to install KT

First make sure you have these installed:

- Python 2.7 (https://www.python.org/)
- MySQL (http://dev.mysql.com/downloads/mysql/)
- Virtualenv (http://www.virtualenv.org/en/latest/)

Create a database with the root user:
```
mysql -u root < scripts/create-db.sql
```

Install KT with this script:
```
./scripts/setup.sh
```

This will:
- create a virtualenv
- install all requirements
- initialize the database
- load test data into it


## How to run KT

```
./scripts/run.sh
```
