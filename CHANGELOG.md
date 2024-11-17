# [0.5.1] (2024-11-17)

## Changes

- Fixed case where Path object is passed to `register_cog` while the database doesnt exist yet, causing an AttributeError.

# [0.5.0] (2024-11-17)

## Changes

- Refactored internal engine code to be more modular and easier to maintain.

## Breaking Changes

- `aquire_db_engine` has been changed to a private method (`_acquire_db_engine`) and is no longer accessible.

# [0.4.0] (2024-18-28)

## Breaking Changes

- Changed `cog` to `cog_instance`
  - Instead of just accepting a `Path` object, you can also pass a `discord.ext.commands.Cog` instance.
- UNC paths are now not supported at all and will raise a UNCPathError.
- Tables will no longer be created outside of running actual migration files.

## Added

- Added ability to pass list of extension names to `register_cog`
- Added `reverse_migration` method
- Added `create_migration` method
- Added `ensure_database_exists` as accessible method
- Added `acquire_db_engine` as accessible method

## Changed

- Cleaned up the `/examples/template_cog` directory showing a more accurate representation of how to use the library.
