# red-postgres

Piccolo Postgres integration for Red-DiscordBot, although it could be used with any dpy bot as an easy wrapper for making postgres with cogs more modular.

![Py](https://img.shields.io/badge/python-v3.11-yellow?style=for-the-badge)
![black](https://img.shields.io/badge/style-black-000000?style=for-the-badge&?link=https://github.com/psf/black)
![license](https://img.shields.io/github/license/Vertyco/red-postgres?style=for-the-badge)

![Forks](https://img.shields.io/github/forks/Vertyco/red-postgres?style=for-the-badge&color=9cf)
![Stars](https://img.shields.io/github/stars/Vertyco/red-postgres?style=for-the-badge&color=yellow)
![Lines of code](https://img.shields.io/tokei/lines/github/Vertyco/red-postgres?color=ff69b4&label=Lines&style=for-the-badge)

# File structure for using with cogs

```
cog-folder/
    ├── db/
    │   ├── migrations/
    │   ├── piccolo_conf.py
    │   ├── piccolo_app.py
    │   ├── tables.py
    ├── __init__.py
    ├── cog.py
```

![SCHEMA](.github/ASSETS/schema.png)

# Cog Usage

```python
import asyncio

from piccolo.engine.postgres import PostgresEngine
from redbot.core import commands
from redbot.core.bot import Red

from red_postgres import register_cog
from .db.tables import MyTable


class PiccoloTemplate(commands.Cog):
    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.db: PostgresEngine = None

    async def cog_load(self):
        asyncio.create_task(self.setup())

    async def setup(self):
        await self.bot.wait_until_red_ready()
        config = await self.bot.get_shared_api_tokens("piccolo")
        self.db = await register_cog(self, config, [MyTable])

    async def cog_unload(self):
        if self.db:
            await self.db.close_connection_pool()
```

The shared api token config for piccolo should be the following:

```json
{
  "database": "database_name",
  "host": "host ip (127.0.0.1)",
  "port": "port (5432)",
  "user": "user123",
  "password": "password123"
}
```

> Note: database name in your config should normally be the default "postgres", this library will automatically handle connecting your cogs to their own database

The register method connects to the database specified in config, creates the a new database with the name of the registering cog, registers any tables, runs any migrations, sets the new engine object to all tables, and returns the raw engine object.

- The name of the database will be the the name of the cog's folder, not the name of the main cog.py file

You can then use your piccolo table methods like so:

```python
count = await MyTable.count()
or
objects = await MyTable.objects().where(MyTable.text == "Hello World")
```

The engine associated with your tables after registering the cog is connected to the database named the same as the cog that registered them, thus using this integration with multiple cogs will not interfere, as each cog will create its own database.

- _If your cog's folder name is `MyCog` then the database will be named `my_cog`_

# Piccolo Configuration Files

Your piccolo configuration files must be setup like so. This is really only used for migrations.

- _When migrations are run, the os environment variables are mocked in subprocess, so there should be no conflicts_

### piccolo_conf.py

```python
import os

from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

DB = PostgresEngine(
    config={
        "database": os.environ.get("POSTGRES_DATABASE"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST"),
        "port": os.environ.get("POSTGRES_PORT"),
    }
)


APP_REGISTRY = AppRegistry(apps=["db.piccolo_app"])
```

### piccolo_app.py

```python
import os

from piccolo.conf.apps import AppConfig, table_finder

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

APP_CONFIG = AppConfig(
    app_name="cog_name",
    table_classes=table_finder(["db.tables"]),
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "migrations"),
)
```

for `table_classes` add in the list of tables you're using

# Local development and making migrations

Handing migrations is up to you, but one way to do it is to make migrations locally like so:

```python
import os
import subprocess
from pathlib import Path

root = Path(__file__).parent
env = os.environ.copy()
env["PICCOLO_CONF"] = "db.piccolo_conf"
env["POSTGRES_HOST"] = "localhost"
env["POSTGRES_PORT"] = "5432"
env["POSTGRES_USER"] = "user"
env["POSTGRES_PASSWORD"] = "password123!"
env["POSTGRES_DATABASE"] = "templatecog"
env["PYTHONIOENCODING"] = "utf-8"


def make():
    migration_result = subprocess.run(
        ["piccolo", "migrations", "new", root.name, "--auto"],
        env=env,
        cwd=root,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.decode()
    print(migration_result)


def run():
    run_result = subprocess.run(
        ["piccolo", "migrations", "forward", root.name],
        env=env,
        cwd=root,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.decode()
    print(run_result)


if __name__ == "__main__":
    make()
    run()

```

You would have a similar file in the root of each of your cog folders, here you would create the migrations to include in your cog folder for users to run when they load up the cog.
