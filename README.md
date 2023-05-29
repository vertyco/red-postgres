# red-postgres

Piccolo Postgres integration for Red-DiscordBot

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
import logging

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
        self.db, migration_result_message = await register_cog(self, config, [MyTable])

    async def cog_unload(self):
        if self.db:
            await self.db.close_connection_pool()
```
The shared api token config for piccolo should be the following:
```json
{
  "database": "database name",
  "host": "host ip",
  "port": "port",
  "user": "user",
  "password": "password"
}
```
The register method connects to the database, creates the database for that cog, registers any tables, runs any migrations, sets the new engine object to all tables, and returns the raw engine object.

You can then use your piccolo table methods like so:
```python
count = await MyTable.count()
or
objects = await MyTable.objects().where(MyTable.text == "Hello World")
```
The engine associated with your tables after registering the cog is connected to the database named the same as the cog that registered them.
 - *If your cog's name is `MyCog` then the database will be named `my_cog`*

# Piccolo Configuration Files
Your piccolo configuration files must be setup like so. This is really only used for migrations.
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