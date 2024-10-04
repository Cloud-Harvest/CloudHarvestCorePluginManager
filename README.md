# Cloud Harvest Plugin Manager
This module is responsible for managing plugins and their configurations. It is designed to work with both the [Cloud Harvest API](https://github.com/Cloud-Harvest/CloudHarvestApi) and the [Cloud Harvest CLI](https://github.com/Cloud-Harvest/CloudHarvestCLI) to load components from plugins such as the [Cloud Harvest AWS Plugin](https://github.com/Cloud-Harvest/CloudHarvestPluginAws).

Organizations and individuals who wish to develop their own plugins should refer to the [Plugin Development Guide](#plugin-development-guide) 
for more information. 

# Table of Contents
- [Cloud Harvest Plugin Manager](#cloud-harvest-plugin-manager)
- [Table of Contents](#table-of-contents)
- [Plugin Development Guide](#plugin-development-guide)
  - [Tasks & Task Chains](#tasks--task-chains)
    - [Base Classes](#base-classes)
    - [Naming Conventions](#naming-conventions)
    - [Task Chain YAML](#task-chain-yaml)
  - [Binaries](#binaries)
  - [Other Languages](#other-languages)
  - [Operating Systems](#operating-systems)
- [How to Implement Your Plugin](#how-to-implement-your-plugin)
  - [Decorators](#decorators)
    - [`register_definition`](#register_definition)
  - [`__registry__.py`](#__registry__py)
- [License](#license)
- [Special License Considerations](#special-license-considerations)

# Plugin Development Guide
The intended purpose of Harvest is to be extensible through plugins so that users can add their own data collectors, data manipulators, and data exporters.

## Tasks & Task Chains
The essence of Harvest is the `Task(Chain)` relationship, where a `Task` is a single unit of work and a `TaskChain` is a collection of `Task`s. 
The `TaskChain` is the primary unit of work in Harvest, and is responsible for orchestrating the execution of `Tasks`. 
In that vien, when developing a plugin, the primary goal is to create a new `Task` or `TaskChain`.

### Base Classes
The `BaseTask` and `BaseTaskChain` are part of [`CloudHarvestCoreTasks`](https://github.com/Cloud-Harvest/CloudHarvestCoreTasks/blob/main/CloudHarvestCoreTasks/base.py) 
which you can add to your project with `requirements.txt` as `CloudHarvestCoreTasks @ git+https://github.com/Cloud-Harvest/CloudHarvestCoreTasks.git@main`.

### Naming Conventions
When creating a new `Task` or `TaskChain`, it is recommended to use the following naming conventions:
- `Task` classes should be named `<Name>Task`
- `TaskChain` classes should be named `<Name>TaskChain`
- For classes with multiple words, use CamelCase, such as `MyTask` or `MyTaskChain`
  - Note that the `Task` and `TaskChain` suffixes are required
  - When called in a `TaskChain` YAML file, the `<Name>` should be 
    - The same as the class name without the suffix
    - Lowercase
    - With underscores between camel case words
- Any registered object should being with a short plugin identifier in its name, such as `aws_` or `gcp_`
  - The exception to this rule is any `Core` component which does not require a prefix.

For example, a class named `MyTask` should be called in a `TaskChain` YAML file as `my`. If this Task is part of the Aws plugin, it would read `aws_my`.

### Task Chain YAML
All TaskChains are defined in YAML files. The following is an example of a TaskChain YAML file:

```yaml
<Name>:                           # TaskChain Name
  description: <Description>      # TaskChain Description
  tasks:
    - <Name>:                     # Task Name
        <ParameterName0>: <ParameterValue0>
        <ParameterName1>: <ParameterValue1>
        
    - <Name>:                     # Task Name
        <ParameterName0>: <ParameterValue0>
        <ParameterName1>: <ParameterValue1>
```

For a practical example of how a Task Chain is written, review this report stored in the [CloudHarvestApi](https://github.com/Cloud-Harvest/CloudHarvestApi/blob/main/CloudHarvestApi/api/blueprints/reports/reports/harvest/nodes.yaml).

## Binaries
If your plugin requires an external binary, such as `aws` or `kubectl`, it will be necessary to include installation runtime in the `main()` function of `post_install.py` in the plugin's root directory. These steps will automatically be executed when the plugin is initialized by Harvest.
> **Note** The `post_install.py` script is not required for all plugins, only those that require external binaries.

> **Note** Consider that some users may be behind a corporate proxy which will make installation of some binaries difficult. Make sure to include a list of require binaries in the plugin's README.

> **WARNING** The `post_install.py` script is executed with root privileges, so be sure to validate the contents of the script before running it.


## Other Languages
Although it is theoretically possible to implement plugins in languages other than Python, be aware that there are no plans to support other languages at this time.

## Operating Systems
Harvest is designed to run on Linux, specifically [Debian](https://www.debian.org/). All Core Cloud Harvest components are 
designed with this in mind. If you are developing a plugin, it is recommended that you test it on a Debian-based system. 
Users who plan to operate Harvest on other operating systems should use Docker or a virtual machine to run Harvest.

To verify the target operating system version, check the contents of the `Dockerfile` in one of the Core Cloud Harvest repositories, 
such as [CloudHarvestApi](https://github.com/Cloud-Harvest/CloudHarvestApi/blob/main/Dockerfile#L1).

# How to Implement Your Plugin
1. Use the [`decorators`](CloudHarvestCorePluginManager/decorators.py) to identify which classes and instances should be added to the Registry. Once added, you can find them using [`Registry.find_definition()` and `Registry.find_instance()`](CloudHarvestCorePluginManager/registry.py).
2. Create a `__registry__.py` in your plugin's directory. This file should contain imports to all classes and instances you want to add to the Registry. Not all classes or instances of classes need be added; only those which the code must reference.

## Decorators
### `register_definition`
```python
# In this example, we add the MyNewTask class to the Registry.
from CloudHarvestCoreTasks.base import BaseTask
from CloudHarvestCorePluginManager.decorators import register_definition

@register_definition(category='task', name='my_new_task', register_instances=False)
class MyNewTask(BaseTask):
  def __init__(self):
    pass

# Elsewhere in the code, use the following to execute your class:
from CloudHarvestCorePluginManager.registry import Registry
my_class = Registry.find(result_key='cls', name='my_new_task')[0](my_arg='my_value')
```

## `__registry__.py`
```python
# Captures definitions
from .tasks import MyNewTask, MyOtherNewTask
from .blueprints import my_blueprint
```

# License
Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

# Special License Considerations
Users and organizations are permitted to design their own plugins for commercial purposes, but are not permitted to 
use [Cloud Harvest](https://github.com/Cloud-Harvest) components or any forks/derivatives thereof in commercial 
endeavors.

For example, if AWS wanted to make its own Harvest plugin for its service which required a commercial license, it 
would be permitted to do so, but would not be permitted to use the 
[Cloud Harvest AWS Plugin](https://github.com/Cloud-Harvest/CloudHarvestPluginAws) as a base for development.
