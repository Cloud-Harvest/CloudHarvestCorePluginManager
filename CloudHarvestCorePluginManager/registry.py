from logging import getLogger
from typing import Any, List

logger = getLogger('harvest')


class Registry:
    definitions = {}
    instances = []

    @staticmethod
    def find_definition(class_name: str = None,
                        is_instance_of: Any = None,
                        is_subclass_of: Any = None,
                        return_all_matching: bool = False) -> List[Any]:
        """
        Finds and returns classes from the Registry's definitions that match the provided criteria.

        Args:
            class_name (str): The name of the class to find.
            is_instance_of (Any): An instance type that the class should be an instance of.
            is_subclass_of (Any): A class that the class should be a subclass of.
            return_all_matching (bool): If True, returns all matching classes. If False, returns only the first matching class.

        Returns:
            List[Any]: A list of matching classes. If no classes match the criteria, returns an empty list.
        """
        result = []

        # Iterate over all classes in the Registry's definitions
        for name, cls in Registry.definitions.items():
            append = False

            # Check if the class name matches the provided class name
            if name == class_name:
                append = True

            # Check if the class is an instance of the provided instance type
            elif is_instance_of and isinstance(cls, is_instance_of):
                append = True

            # Check if the class is a subclass of the provided class
            elif is_subclass_of and issubclass(cls, is_subclass_of):
                append = True

            # If the class matches any of the criteria, add it to the result list
            if append:
                result.append(cls)

                # If return_all_matching is False, stop searching after finding the first matching class
                if not return_all_matching:
                    break

        return result

    @staticmethod
    def find_instance(class_name: str = None,
                      is_instance_of: Any = None,
                      is_subclass_of: Any = None,
                      return_all_matching: bool = False) -> List[Any]:
        """
        Finds and returns instances from the Registry's instances that match the provided criteria.

        Args:
            class_name (str): The name of the class of the instance to find.
            is_instance_of (Any): An instance type that the instance should be an instance of.
            is_subclass_of (Any): A class that the instance's class should be a subclass of.
            return_all_matching (bool): If True, returns all matching instances. If False, returns only the first matching instance.

        Returns:
            List[Any]: A list of matching instances. If no instances match the criteria, returns an empty list.
        """
        result = []

        # Iterate over all instances in the Registry's instances
        for instance in Registry.instances:
            append = False

            # Check if the instance's class name matches the provided class name
            if instance.__class__.__name__ == class_name:
                append = True

            # Check if the instance is an instance of the provided instance type
            elif is_instance_of and isinstance(instance, is_instance_of):
                append = True

            # Check if the instance's class is a subclass of the provided class
            elif is_subclass_of and issubclass(instance.__class__, is_subclass_of):
                append = True

            # If the instance matches any of the criteria, add it to the result list
            if append:
                result.append(instance)

                # If return_all_matching is False, stop searching after finding the first matching instance
                if not return_all_matching:
                    break

        return result

    @staticmethod
    def register_objects():
        """
        Loads all packages with the prefix 'CloudHarvestPlugin' and imports the contents of each package's '__register__.py' file.
        """
        import pkgutil
        import importlib
        import site

        # Get the path of the site-packages directory
        site_packages_path = site.getsitepackages()[0]

        # Iterate over all modules in the site-packages directory
        for _, package_name, _ in pkgutil.iter_modules([site_packages_path]):

            # Check if the package name starts with 'CloudHarvestPlugin'
            if package_name.startswith('CloudHarvestPlugin'):

                # Try to import the '__register__.py' file from the package
                try:
                    importlib.import_module(f'{package_name}.__register__')

                except ImportError:
                    # If the '__register__.py' file does not exist, skip this package
                    continue
