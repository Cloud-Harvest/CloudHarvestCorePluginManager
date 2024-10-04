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
>>>         'instances': []
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
    def add(name: str, category: str = None, cls: Any = None, instances: List[Any] = None) -> None:
        """
        Adds the provided object to the Registry.

        :param name: The name of the object to add.
        :param category: The category of the object to add.
        :param cls: The class of the object to add.
        :param instances: One or more instantiated objects to add to the Registry.
        """

        # Check if the object already exists in the Registry
        if not Registry._OBJECTS.get(name):
            if not category or not cls:
                raise ValueError('Category and class must be provided when adding a new object to the Registry.')

            else:
                # Add the object to the Registry
                Registry._OBJECTS[name.lower()] = {
                    'category': category.lower(),
                    'cls': cls,
                    'instances': []
                }

        # If instances are provided, add them to the object's instances list, but only if the object is not already in the
        # list. This prevents duplicate instances from being added.
        if instances:
            [
                Registry._OBJECTS[name]['instances'].append(instance)
                for instance in instances
                if instance not in Registry._OBJECTS[name]['instances']
            ]

        return None

    @staticmethod
    def clear() -> None:
        """
        Clears the Registry of all objects.
        """

        Registry._OBJECTS.clear()

        return None

    @staticmethod
    def find(result_key: str, name: str = None, category: str = None, cls: Any = None, limit: int = 1) -> List[Any]:
        """
        Finds and returns the result_key based on the provided criteria.

        :param result_key: The key to return.
        :param name: The name of the object to find.
        :param category: The category of the object to find.
        :param cls: The class of the object to find. If provided, the object must be an instance or subclass of this class.
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

        result = []

        for _name, _config in Registry._OBJECTS.items():
            if name and name.lower() != _name:
                continue

            if category and category.lower() != _config['category']:
                continue

            if cls and cls is _config['cls']:
                continue

            if result_key == 'name':
                result.append(_name)

            else:
                if _config.get(result_key):
                    if isinstance(_config[result_key], list):
                        result.extend(_config[result_key])

                    else:
                        result.append(_config[result_key])

            if len(result) >= limit:
                break

        return result

    @staticmethod
    def remove(name: str = None, category: str = None, cls: Any = None, instances: List[Any] = None) -> None:
        """
        Removes the object with the provided name from the Registry.

        :param name: The configuration name to remove.
        :param category: The category of the object to remove.
        :param cls: The class of the object to remove.
        :param instances: One or more instances of the object to remove.
        """

        if name:
            name = name.lower()
            if Registry._OBJECTS.get(name):
                Registry._OBJECTS.pop(name)

        if category or cls or instances:
            for _name in tuple(Registry._OBJECTS.keys()):
                if category and category.lower() == Registry._OBJECTS[_name]['category']:
                    Registry._OBJECTS.pop(_name)
                    continue

                if cls and cls is Registry._OBJECTS[_name]['cls']:
                    Registry._OBJECTS.pop(_name)
                    continue

                if instances:
                    for instance in instances:
                        if instance in Registry._OBJECTS[_name]['instances']:
                            Registry._OBJECTS[_name]['instances'].remove(instance)

        return None
