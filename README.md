# Kritikus Tömeg

[Kritikus Tömeg](https://kritikustomeg.org/) is a Hungarian movie site, community, database, recommendation engine.


## How to install KT

You need [Docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) installed on your machine.

Install KT with this script:
```
./scripts/setup.sh
```

This will:
- build a Docker image (called `kt-dev`) as a dev environment that contains all required Python dependencies
- create a Docker volume (called `kt-db`) that contains the test database for KT development


## How to run KT

Just run this script:

```
./scripts/start-dev.sh
```

and open http://localhost:8000/ in the browser.

You can check the logs with:

```
./scripts/show-logs.sh
```

And stop KT with:

```
./scripts/stop-dev.sh
```


## Adding/changing Python requirements

If you add/change anything in `requirements.txt`, don't forget to rebuild the dev image:

```
./scripts/build-dev-image.sh
```


## Resetting the database

If you want to reset your database for any reason, just run:

```
./scripts/init-dev-db.sh
```


## Developer guide

If you want to participate, here are some rules and guidelines.

Even though KT is Hungarian, code (especially open source code) should always be English. Someday, somewhere (maybe) some Danish guys might decide to start *Kritisk masse* (or the Russians *Критическая масса*). If code is English, they only need to translate URLs and templates (and build a database) (and of course raise a community).

For Hungarian communication and coordination use [this topic](https://kritikustomeg.org/forum/187/kritikus-kod) on KT.

Please use "standard" coding style:

- use only space for indentation (4 of them per level)
- lines should end with `LF` (`\n`, `\x0A`)
- everything (code, templates, database) is unicode, `utf-8` (collation: `utf8_hungarian_ci`)

Otherwise follow PEP-8 and use pylint.
