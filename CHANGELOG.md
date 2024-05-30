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
