# red-postgres

Piccolo Postgres integration for Red-DiscordBot, although it could be used with any dpy bot as an easy wrapper for making postgres with cogs more modular.

[![PyPi](https://img.shields.io/pypi/v/red-postgres)](https://pypi.org/project/red-postgres/)
[![Pythons](https://img.shields.io/pypi/pyversions/red-postgres)](https://pypi.org/project/red-postgres/)

![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?logo=postgresql&logoColor=white)
![Red-DiscordBot](https://img.shields.io/badge/Red%20DiscordBot-V3.5-red)

![black](https://img.shields.io/badge/style-black-000000?link=https://github.com/psf/black)
![license](https://img.shields.io/github/license/Vertyco/red-postgres)

# Install

```python
pip install red-postgres
```

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

![SCHEMA](https://raw.githubusercontent.com/vertyco/red-postgres/main/.github/ASSETS/schema.png)

# Cog Usage

```python
import asyncio
from pathlib import Path

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
        config = await self.bot.get_shared_api_tokens("postgres")
        self.db = await register_cog(self, config, [MyTable])

    async def cog_unload(self):
        if self.db:
            self.db.pool.terminate()
```

The config for piccolo should have the following keys:

```json
{
  "database": "postgres",  # Replace with your maintenance database
  "host": "127.0.0.1",  # Replace with your host
  "port": "5432",  # Replace with your port
  "user": "postgres",  # Replace with your user
  "password": "postgres"  # Replace with your password
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

- _If your cog's folder name is `MyCog` then the database will be named `mycog`_

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
    app_name="cogname",  # Replace with your cog name
    table_classes=table_finder(["db.tables"]),
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "migrations"),
)
```

for `table_classes` add in the list of tables you're using

# Local development and making migrations

Handing migrations is up to you, but one way to do it is to make migrations locally like so:

First make an `.env` file in the root of your cog's folder.

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DATABASE=postgres
```

Then create a `build.py` file in your cog folder.

```python
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from engine import engine

load_dotenv()

config = {
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "database": os.environ.get("POSTGRES_DATABASE"),
    "host": os.environ.get("POSTGRES_HOST"),
    "port": os.environ.get("POSTGRES_PORT"),
}

root = Path(__file__).parent


async def main():
    created = await engine.ensure_database_exists(root, config)
    print(f"Database created: {created}")
    description = input("Enter a description for the migration: ")
    print(await engine.create_migrations(root, config, True, description.replace('"', "")))
    print(await engine.run_migrations(root, config, True))


if __name__ == "__main__":
    asyncio.run(main())

```

You would have a similar file in the root of each of your cog folders, here you would create the migrations to include in your cog folder for users to run when they load up the cog.
