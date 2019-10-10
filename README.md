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


## How to use Visual Studio Code

Install [Visual Studio Code](https://code.visualstudio.com/download).

Install the [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) and [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extensions.

Open KT in VSCode: File / Open... / choose the KT folder.

In the Command Palette (press `F1`) choose `Remote-Containers: Reopen in Container`

This will create two Docker containers (one for KT, one for MySQL), if they don't exist already. Now you can:

- navigate the code (dependencies are properly included)
- run/debug KT from VSCode: Debug / Start Debugging (`F5`)

If you want to stop running KT: Debug / Stop Debugging.

If you want to stop developing: `Remote-Containers: Reopen Locally`. This will stop the containers.

Note: you cannot use `./scripts/start-dev.sh` and `Remote-Containers: Reopen in Container` at the same time. If you try, it will fail because port 8000 on your host machine cannot be forwarded to two different containers. And it might also corrupt your database volume (`kt-db`), because two MySQL server instances will try to use it. If the latter happens, you can reset the database with `./scripts/init-dev-db.sh`.


## Developer guide

If you want to participate, here are some rules and guidelines.

Even though KT is Hungarian, code (especially open source code) should always be English. Someday, somewhere (maybe) some Danish guys might decide to start *Kritisk masse* (or the Russians *Критическая масса*). If code is English, they only need to translate URLs and templates (and build a database) (and of course raise a community).

For Hungarian communication and coordination use [this topic](https://kritikustomeg.org/forum/187/kritikus-kod) on KT.

Please use "standard" coding style:

- use only space for indentation (4 of them per level)
- lines should end with `LF` (`\n`, `\x0A`)
- everything (code, templates, database) is unicode, `utf-8` (collation: `utf8_hungarian_ci`)

Otherwise follow PEP-8 and use pylint.
