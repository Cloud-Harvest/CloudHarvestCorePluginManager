# 0.4.0
- Updated the `register_definition()` decorator to accept meta argument `tags`.
  - `tags` is a list of strings that can be used to further categorize classes.
  - the `Registry.find()` method was updated to include searches by Tags.
    - When searching by tags:
      - the search is an OR operation meaning that at least one tag must match.
      - the search is case-sensitive.
    - `result_key` can now be set to `*` which returns the entire record for each match including metadata like `tags` and `category`.
- Moved all `register_*` methods out of `functions.py` and into `registry.py`. 
- Added the `register_task_templates()`
  - This method registers the contents of YAML files stored in CloudHarvest `template` directories throughout the application and its packages.
  - The `cls` is populated by the actual content of the file, a dictionary.
- `Registry.add()` now registers objects using a `category-task` convention
  - This allows objects with the same name to be registered in different categories (ie `report` and `service` templates)
  - Updated associated methods accordingly
  - `category` is now required when registering objects

# 0.3.1
- Added `decorators.get_class_module_metadata()` which attaches module-level metadata to classes

# 0.3.0
- Completely rewrote how registered objects are stored and retrieved
  - Objects are now stored in `registry.Registry._OBJECTS` as a dictionary with the configuration name as the key.
  - New methods are: `add()`, `find()`, and `remove()`
  - Stored objects now include keys `category`, `cls`, and `instances`
- Removed `@register_instance` decorator
  - `@register_definition` now registers the class and records the instances when `register_instances=True`


# 0.2.4
- `register_definition()` was updated to require the `name: str` parameter 
  - This change was made so that classes could be registered with a name that is different from the class name.
  - We also observed that using `str.lower().title()` was not consistent, so this change means we always know what the class' registered name is will be.

# 0.2.3
- Changed `register_objects()` so that it will scan packages beginning with `CloudHarvest` and not `CloudHarvestPlugin`.
  - This was preventing `CloudHarvestCore` packages from being read when `register_objects()` was called
  - We anticipate any plugin to being package names with `CloudHarvest` and include a `__register__.py` file

# 0.2.2
- Added a performance improvement to `find_definition()` which uses `class_name` as a lookup to the `Registry.definitions.keys()`

# 0.2.1
- Fixed an issue where the `find` methods would not return the correct class

# 0.2.0
- Complete rewrite of the plugin system
- `PluginRegistry` is now `Registry`
- Added [`decorators`](CloudHarvestCorePluginManager/decorators.py)
- Replaced `find_classes()` with `find_definition()` (classes) and `find_instance()` (instantiated classes)
- Updated the README

# 0.1.6
- Added try/excepts to keep plugin install errors from being breaking

# 0.1.5
- Expanded changes made in 0.1.4

# 0.1.4
- `PluginRegistry` will now skip files/modules beginning with `__`
- Added CHANGELOG.md
