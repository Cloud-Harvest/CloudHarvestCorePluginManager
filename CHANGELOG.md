# 2024-05-29
## 0.2.0
- Complete rewrite of the plugin system
- `PluginRegistry` is now `Registry`
- Added [`decorators`](CloudHarvestCorePluginManager/decorators.py)
- Replaced `find_classes()` with `find_definition()` (classes) and `find_instance()` (instantiated classes)
- Updated the README

# 2024-05-28
## 0.1.6
- Added try/excepts to keep plugin install errors from being breaking

## 0.1.5
- Expanded changes made in 0.1.4

## 0.1.4
- `PluginRegistry` will now skip files/modules beginning with `__`
- Added CHANGELOG.md
