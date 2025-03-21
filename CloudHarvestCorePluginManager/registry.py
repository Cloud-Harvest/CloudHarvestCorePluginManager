"""
The Registry module is responsible for storing references and instances of different classes and _REGISTRY. In order to
register an object, it is necessary to take the following steps:
1. Provide the appropriate @decorator in .decorators in the class definition.
2. Import all decorated classes into __register.py__ in the package's source code root directory.
3. Call register_objects() during application load

Registry Structure
The Registry is a dictionary of dictionaries that stores the following information about each object:

Key         | Default   | Description
------------|-----------|------------
name        | None      | The name of the object. This must be a unique identifier. For example, the FileTask is known as 'file'. No other object can have the name 'file'.
category    | None      | The category of the object.
cls         | None      | The class of the object.
instances   | []        | A list of instances of the object.


Object Categories
All registered objects are categorized into one of the following which must be provided in lower case characters:

Category  | Description
----------|------------
blueprint | A flask blueprint used to extend the functionality of the API.
task      | Represents a task that can be executed.

Custom categories can be provided as needed.

Example
>>> Registry._OBJECTS = {
>>>     'name': {
>>>         'category': 'task',
>>>         'cls': Any,
>>>         'instances': [],
>>>         'tags': []
>>>     }
>>> }

"""

from logging import getLogger
from typing import Any, List

logger = getLogger('harvest')


class Registry:
    """
    This static class represents the Registry, which is used to store references and instances of different classes and
    objects. _OBJECTS should not be accessed directly. Instead, use the add(), find(), and remove() methods to interact
    with the Registry.
    """

    _OBJECTS = {}

    @staticmethod
    def add(category: str, name: str, cls: Any = None, instances: List[Any] = None, tags: List[str] = None) -> dict:
        """
        Adds the provided object to the Registry.

        Arguments
        category (str): The category of the object to add.
        name (str): The name of the object to add.
        cls (Any): The class of the object to add.
        instances (List[Any]): One or more instantiated objects to add to the Registry.
        tags (List[str]): A list of tags to associate with the object.

        """

        registered_name = f'{category}-{name}'.lower()

        # Check if the object already exists in the Registry
        if not Registry._OBJECTS.get(registered_name):
            # Add the object to the Registry
            Registry._OBJECTS[registered_name] = {
                'name': name.lower(),
                'category': category.lower(),
                'cls': cls,
                'instances': [],
                'tags': tags or []
            }

            logger.debug(f'Registered {category.lower()}: {name}')

        # If instances are provided, add them to the object's instances list, but only if the object is not already in the
        # list. This prevents duplicate instances from being added.
        if instances:
            [
                Registry._OBJECTS[registered_name]['instances'].append(instance)
                for instance in instances
                if instance not in Registry._OBJECTS[registered_name]['instances']
            ]

        return Registry._OBJECTS.get(registered_name)

    @staticmethod
    def clear() -> None:
        """
        Clears the Registry of all objects.
        """

        Registry._OBJECTS.clear()
        logger.debug('Registry cleared.')

        return None

    @staticmethod
    def find(result_key: str,
             category: str = None,
             name: str = None,
             cls: Any = None,
             tags: List[str] = None,
             limit: int or None = 1) -> List[Any]:
        """
        Finds and returns the result_key based on the provided criteria.

        :param result_key: The key to return.
        :param category: The category of the object to find. This is a regex expression.
        :param name: The name of the object to find.
        :param cls: The class of the object to find. If provided, the object must be an instance or subclass of this class.
        :param tags: A list of tags to filter the results by.
        :param limit: Maximum matching items to return.
        :return: The result_key of objects matching the provided criteria.

        Example:
        >>> # Returns the instances of the class with the name 'my_class'.
        >>> Registry.find(result_key='instances', name='my_class')
        >>> [instance1, instance2, ...]

        >>> # Returns the classes of the objects with the category 'task'.
        >>> Registry.find(result_key='cls', category='task')
        >>> [class1, class2, ...]

        >>> # Return a class with the name 'my_class' and category 'task'.
        >>> Registry.find(result_key='cls', name='my_class', category='task', limit=1)
        >>> [class1]
        """
        from re import fullmatch, IGNORECASE

        result = []

        for registered_name, config in Registry._OBJECTS.items():
            # Although 'category' comes first in the registered_name, names are more likely to be unique. Therefore, it
            # is more efficient to check the name first.
            if name and name.lower() != config['name']:
                continue

            if category and not fullmatch(category, config['category'], flags=IGNORECASE):
                continue

            if cls and not issubclass(config['cls'], cls):
                continue

            if tags and not any(tag in config['tags'] for tag in tags):
                continue

            # If the result_key is '*', return the entire configuration
            if result_key == '*':
                result.append(config)

            # Otherwise, return the specified key from the configuration
            else:
                if config.get(result_key):
                    if isinstance(config[result_key], list):
                        result.extend(config[result_key])

                    else:
                        result.append(config[result_key])

            if limit and len(result) >= limit:
                break

        return result

    @staticmethod
    def remove(name: str, category: str) -> None:
        """
        Removes the object with the provided name from the Registry.

        :param name: The configuration name to remove.
        :param category: The category of the object to remove.
        """

        registered_name = f'{category}-{name}'.lower()

        if Registry._OBJECTS.get(registered_name):
            Registry._OBJECTS.pop(registered_name)

            logger.debug(f'Removed {registered_name} from the Registry.')

        return None

def register_all():
    """
    Executes all methods in this file that start with 'register_' (except for this method).
    """

    methods = {
        name: method
        for name, method in globals().items()
        if name.startswith('register_') and name != 'register_all'
    }

    for name, method in methods.items():
        if name.startswith('register_') and name != 'register_all':
            logger.info(f'Executing: {name}')
            method()

def register_objects():
    """
    Loads all packages with the prefix 'CloudHarvest' and imports the contents of each package's '__register__.py' file.
    This allows the decorators to register the classes in the Registry.
    """
    import pkgutil
    import importlib
    import site

    # Get the path of the site-packages directory
    site_packages_path = site.getsitepackages()[0]

    # Iterate over all modules in the site-packages directory
    for _, package_name, _ in pkgutil.iter_modules([site_packages_path]):

        # Check if the package name starts with 'CloudHarvest'
        if package_name.startswith('CloudHarvest'):

            # Try to import the '__register__.py' file from the package
            try:
                importlib.import_module(f'{package_name}.__register__')

            except ImportError:
                # If the '__register__.py' file does not exist, skip this package
                continue

            else:
                logger.info(f'Loaded package: {package_name}')


def register_task_templates():
    """
    Scans the current project directory and all site-packages directories for template files and registers them in the
    Registry. Template files must be
        - In YAML format and have a '.yaml' extension.
        - Located in a package with the prefix 'CloudHarvest'.
        - Be located in a 'templates' directory of the package.

    Templates are named based on their directory path relative to the 'templates' directory. For example, a template file
    located at 'CloudHarvestPluginExample/templates/example.yaml' would be registered as 'example'.
    """

    import os
    import yaml
    import site

    templates_dict = {}

    def scan_directory(directory: str):
        for root_path, _, files in os.walk(directory):
            if 'templates' in root_path:
                for file in files:
                    if file.endswith('.yaml'):
                        file_path = os.path.join(root_path, file)
                        split_path = file_path.split(os.sep)
                        category_position = split_path.index('templates') + 1
                        category = split_path[category_position]
                        name = '.'.join(split_path[category_position + 1:]).replace('.yaml', '')
                        unique_name = f'{category}.{name}'

                        if templates_dict.get(unique_name):
                            logger.debug(f'Found duplicate template: {unique_name}')
                            continue

                        with (open(file_path, 'r') as yaml_file):
                            templates_dict[unique_name] = yaml.load(yaml_file, Loader=yaml.FullLoader)

    # Scan the current project directory
    scan_directory(os.getcwd())

    # Scan the site-packages directories
    for site_packages_path in site.getsitepackages():
        for root, dirs, _ in os.walk(site_packages_path):
            for dir_name in dirs:
                if dir_name.startswith('CloudHarvest'):
                    scan_directory(os.path.join(root, dir_name))

    # Register the located templates
    for template_name, template_data in templates_dict.items():

        # The first position in the template name is the category, and the rest is the registration name
        template_category = template_name.split('.')[0]
        template_registration_name = '.'.join(template_name.split('.')[1:])

        Registry.add(name=template_registration_name,
                     category=f'template_{template_category}',
                     cls=template_data)
