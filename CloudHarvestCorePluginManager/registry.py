from logging import getLogger
from typing import Any, Literal

logger = getLogger('harvest')


class PluginRegistry:
    """
    The PluginRegistry class is responsible for managing plugins in the application. It provides methods to install, initialize, and retrieve plugins.

    Attributes:
        classes (dict): A dictionary to store uninstantiated classes of the plugins. Retrieve them using PluginRegistry.find_classes().
        instantiated_classes (dict): A dictionary to store instantiated classes of the plugins.
        plugins (dict): A dictionary to store the plugins, populated from HarvestConfiguration.plugins.
                        The format of the dictionary is {package_name_or_url: version_or_branch}.
                        When the package_name_or_url begins with 'https://' it is considered a git repository and version_or_branch is the branch name.
                        Otherwise, it is considered a PyPI package and version_or_branch is the version number.
        modules (dict): A dictionary to store loaded modules.
    """

    classes = {}
    instantiated_classes = {}
    plugins = {}
    modules = {}

    @staticmethod
    def _initialize_all_plugins():
        """
        Initializes all plugins in the PluginRegistry. It imports all packages in the site-packages directory that
        start with 'CloudHarvest' and are not already imported. Then, it gets all classes within the module.
        """

        import os
        import glob
        import site
        import sys
        import importlib

        # Get the path of the site-packages directory
        site_packages_path = site.getsitepackages()[0]

        # Create a pattern for directories starting with 'CloudHarvest'
        pattern = os.path.join(site_packages_path, 'CloudHarvest*')

        # Iterate over all directories in the site-packages directory that match the pattern
        for directory in glob.glob(pattern):

            # Get the package name from the directory path
            package_name = os.path.basename(directory)

            # Check if the package is already imported
            if package_name not in sys.modules and 'dist-info' not in package_name:
                # If the package is not already imported, import it
                PluginRegistry.modules[package_name] = importlib.import_module(package_name)

                # Get all classes within the module
                PluginRegistry.classes[package_name] = PluginRegistry.register_all_classes_in_package(
                    PluginRegistry.modules[package_name])

        return PluginRegistry

    @staticmethod
    def find_classes(class_name: str = None,
                     package_name: str = None,
                     is_instance_of: Any = None,
                     is_subclass_of: Any = None,
                     return_all_matching: bool = False,
                     return_type: Literal['both', 'classes', 'instantiated'] = 'both') -> Any:
        """
        Retrieves a class or classes from the PluginRegistry based on the provided parameters.

        Args:
            class_name (str): The name of the class.
            package_name (str, optional): The name of the package. If specified, only classes from this package are considered.
            is_instance_of (Any, optional): If specified, only classes that are instances of this class are considered.
            is_subclass_of (Any, optional): If specified, only classes that are subclasses of this class are considered.
            return_all_matching (bool, optional): If True, return all classes that match the provided parameters.
                                                  If False, return the first matching class.
            return_type (str, optional): If 'classes', return classes.
                                         If 'instantiated', return instantiated classes.
                                         If 'both', return both classes and instantiated classes.

        Returns:
            The class or classes if they exist in the PluginRegistry and match the provided parameters; otherwise, None.
        """

        matching_classes = []
        matching_instances = []

        if return_type in ['classes', 'both']:
            # Iterate over all packages in the PluginRegistry.classes
            for pr_package_name, pr_classes in PluginRegistry.classes.items():
                # Skip if package_name is specified and does not match the current package
                if package_name and pr_package_name != package_name:
                    continue

                # Iterate over all classes in the package
                for cls_name, cls in pr_classes.items():
                    # Skip if class_name does not match the current class
                    if class_name is not None and cls_name != class_name:
                        continue

                    # Skip if is_instance_of is specified and the current class is not an instance of it
                    if is_instance_of and not isinstance(cls, is_instance_of):
                        continue

                    # Skip if is_subclass_of is specified and the current class is not a subclass of it
                    if is_subclass_of and not issubclass(cls, is_subclass_of):
                        continue

                    # If all conditions are met, add the current class to the list of matching classes
                    matching_classes.append(cls)

                    # If return_all_matching is False, return the first matching class
                    if not return_all_matching and return_type == 'classes':
                        return matching_classes[0]

        if return_type in ['instantiated', 'both']:
            # Iterate over all packages in the PluginRegistry.instantiated_classes
            for pr_package_name, pr_modules in PluginRegistry.instantiated_classes.items():
                # Skip if package_name is specified and does not match the current package
                if package_name and pr_package_name != package_name:
                    continue

                # Iterate over all modules in the package
                for module_name, items in pr_modules.items():
                    # Iterate over all items in the module
                    for item in items:
                        # Skip if class_name does not match the current item
                        if class_name is not None and item.__class__.__name__ != class_name:
                            continue

                        # Skip if is_instance_of is specified and the current item is not an instance of it
                        if is_instance_of and not isinstance(item, is_instance_of):
                            continue

                        # Skip if is_subclass_of is specified and the current item is not a subclass of it
                        if is_subclass_of and not issubclass(item.__class__, is_subclass_of):
                            continue

                        # If all conditions are met, add the current item to the list of matching classes
                        matching_instances.append(item)

                        # If return_all_matching is False, return the first matching class
                        if not return_all_matching and return_type == 'instantiated':
                            return matching_instances[0]

        # If return_all_matching is True, return all matching classes
        if return_all_matching or return_type == 'both':
            return matching_classes + matching_instances

        return None

    @staticmethod
    def install(quiet: bool = False):
        """
        Installs all plugins in PluginRegistry.plugins. Once all plugins are installed, they are initialized.

        Args:
            quiet (bool, optional): If True, suppresses logging output. Default is False.
        """

        if not PluginRegistry.plugins:
            logger.warning('No plugins to install.')
            return

        from subprocess import run, PIPE
        from sys import stdout

        route_output = PIPE if quiet else stdout

        # construct the pip install command
        args = ['pip', 'install']
        packages_to_install = []

        # iterate over all plugins and add them to the list of packages to install
        for package_name_or_url, version_or_branch in PluginRegistry.plugins.items():
            # check if the package is a git repository
            if package_name_or_url.startswith('https://'):
                packages_to_install.append(f'git+{package_name_or_url}@{version_or_branch}')

            # if the package is not a git repository, add it to the list of packages to install
            else:
                packages_to_install.append(f'{package_name_or_url}{version_or_branch}')

        args.extend(packages_to_install)

        logger.debug(f'Installing plugins: {" ".join(args)}')
        process = run(args=args, stdout=route_output, stderr=route_output)

        if process.returncode != 0:
            logger.error(f'Plugin installation failed with error code {process.returncode}')

            if route_output == PIPE:
                logger.error(
                    f'Plugin installation output:' + process.stdout.decode('utf-8') + process.stderr.decode('utf-8'))

        else:
            if route_output == PIPE:
                logger.debug(
                    f'Plugin installation output:' + process.stdout.decode('utf-8') + process.stderr.decode('utf-8'))

            PluginRegistry._initialize_all_plugins()

    @staticmethod
    def register_all_classes_in_package(package):
        """
        Retrieves all classes from a package.

        Args:
            package: The package to retrieve classes from.

        Returns:
            A dictionary of classes in the package.
        """

        import pkgutil
        import importlib
        import inspect

        classes = {}
        for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and package.__name__ in obj.__module__:
                    classes[name] = obj

        return classes

    @staticmethod
    def register_all_classes_by_path(path: str, override_package_name: str = None):
        """
        Retrieves all classes from a package.

        Args:
            path (str): The path to the package to retrieve classes from.
            override_package_name (str, optional): The name of the package. If not provided, it is derived from the path.

        Returns:
            A dictionary of classes in the package.
        """

        import os
        import pkgutil
        import importlib
        import inspect

        classes = {}
        package_name = os.path.basename(os.path.abspath(path))

        # Iterate over all modules in the package
        for _, module_name, _ in pkgutil.iter_modules([path]):

            # Import the module
            module = importlib.import_module(f"{package_name}.{module_name}")

            # Iterate over all classes in the module
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and obj.__module__ == module.__name__:
                    classes[name] = obj

        PluginRegistry.classes[override_package_name or package_name] = classes
        return classes

    @staticmethod
    def register_instantiated_classes_by_path(path: str, override_package_name: str = None) -> dict:
        """
        Registers all instantiated classes from a given path into the PluginRegistry's instantiated_classes dictionary.

        This method scans all Python files in the provided path, imports them as modules, and registers all objects that are instances of a class (excluding the classes themselves). The method ignores private and special attributes (those starting with '__').

        The results are stored in the instantiated_classes dictionary, where the key is the package name derived from the provided path, and the value is another dictionary. In this inner dictionary, the key is the module name and the value is a list of instantiated classes from that module.

        Args:
            path (str): The path to retrieve classes from. This should be a directory containing Python files.
            override_package_name (str, optional): The name of the package within the PluginRegistry. If not provided, it is derived from the path.

        Returns:
            dict: A dictionary where the key is the module name and the value is a list of instantiated classes in the module.
        """

        from os.path import abspath, basename
        from importlib import import_module
        from inspect import isclass

        results = {}
        from glob import glob
        package_name = basename(abspath(path))

        py_files = glob(path + '/**/*.py', recursive=True)
        for file in py_files:
            if '__init__.py' in file:
                continue

            # Remove the '.py' extension from the filename to get the module name
            module_name = file[:-3].replace('/', '.').replace('..', '')

            # Log the loading of the module
            logger.info(f'Loading module: {file}')

            # Import the module
            module = import_module(module_name, package=package_name)

            # Iterate over all items in the module
            for item in dir(module):

                # skip private and special attributes
                if item.startswith('__'):
                    continue

                # Get the object associated with the item
                obj = getattr(module, item)

                # Add the object to the results list if it is a class
                if isinstance(obj, object) and not isclass(obj):
                    if results.get(module.__name__) is None:
                        results[module.__name__] = []

                    results[module.__name__].append(obj)

        # Add the results list to the instantiated_classes dictionary with the source module name as the key
        PluginRegistry.instantiated_classes[override_package_name or package_name] = results

        return results
