# Cloud Harvest Plugin Manager
This module is responsible for managing plugins and their configurations. It is designed to work with both the [Cloud Harvest API](https://github.com/Cloud-Harvest/CloudHarvestApi) and the [Cloud Harvest CLI](https://github.com/Cloud-Harvest/CloudHarvestCLI) to load components from plugins such as the [Cloud Harvest AWS Plugin](https://github.com/Cloud-Harvest/CloudHarvestPluginAws).

Organizations and individuals who wish to develop their own plugins should refer to the [Plugin Development Guide](#plugin-development-guide) 
for more information. 

# Table of Contents
- [Cloud Harvest Plugin Manager](#cloud-harvest-plugin-manager)
- [Table of Contents](#table-of-contents)
- [Plugin Development Guide](#plugin-development-guide)
- [License](#license)

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

For example, a class named `MyTask` should be called in a `TaskChain` YAML file as `my`. A practical example of this is `CacheAggregateTask` which is called as `cache_aggregate`.

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

# How Harvest Uses Your Plugin
When Harvest loads a plugin, it will identify and store all classes in the `[PluginRegistry](./CloudHarvestCorePluginManager/registry.py)`, 
a key component of this repository. Once the plugin is loaded, Harvest will be able to instantiate and execute the 
classes within the plugin by calling `PluginRegistry.get_class_by_name()` which, in turn, is called from a TaskChain's 
templating engine.

```
TaskChain Yaml File -> TaskChain Templating Engine -> PluginRegistry.get_class_by_name() -> Your Plugin Class
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
