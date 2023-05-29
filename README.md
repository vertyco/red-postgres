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

# piccolo_conf.py
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

# piccolo_app.py
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