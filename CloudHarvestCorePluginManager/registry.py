from logging import getLogger
from typing import Any

logger = getLogger('harvest')


class PluginRegistry:
    """
    The PluginRegistry class is responsible for managing plugins in the application. It provides methods to install, initialize, and retrieve plugins.

    Attributes:
        classes (dict): A dictionary to store uninstantiated classes of the plugins. Retrieve them using PluginRegistry.find_classes().
        plugins (dict): A dictionary to store the plugins, populated from HarvestConfiguration.plugins.
        modules (dict): A dictionary to store loaded modules.
    """

    classes = {}
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
                PluginRegistry.classes[package_name] = PluginRegistry._register_all_classes_in_package(PluginRegistry.modules[package_name])

        return PluginRegistry

    @staticmethod
    def _register_all_classes_in_package(package):
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
    def find_classes(class_name: str,
                     package_name: str = None,
                     is_instance_of: Any = None,
                     is_subclass_of: Any = None,
                     return_all_matching: bool = False) -> Any:
        """
        Retrieves a class or classes from the PluginRegistry based on the provided parameters.

        Args:
            class_name (str): The name of the class.
            package_name (str, optional): The name of the package. If specified, only classes from this package are considered.
            is_instance_of (Any, optional): If specified, only classes that are instances of this class are considered.
            is_subclass_of (Any, optional): If specified, only classes that are subclasses of this class are considered.
            return_all_matching (bool, optional): If True, return all classes that match the provided parameters. If False, return the first matching class.

        Returns:
            The class or classes if they exist in the PluginRegistry and match the provided parameters; otherwise, None.
        """

        matching_classes = []

        # Iterate over all packages in the PluginRegistry
        for pr_package_name, pr_classes in PluginRegistry.classes.items():
            # Skip if package_name is specified and does not match the current package
            if package_name and pr_package_name != package_name:
                continue

            # Iterate over all classes in the package
            for cls_name, cls in pr_classes.items():
                # Skip if class_name does not match the current class
                if cls_name != class_name:
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
                if not return_all_matching:
                    return matching_classes[0]

        # If return_all_matching is True, return all matching classes
        return matching_classes if matching_classes else None

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

        # configure a cache directory for pip
        from pathlib import Path
        cache_path = Path('./app/pip/cache')
        cache_path.mkdir(parents=True, exist_ok=True)

        from subprocess import run, PIPE
        from sys import stdout

        route_output = PIPE if quiet else stdout

        args = ['pip', 'install']
        args.extend([f'git+{url}@{branch}' for url, branch in PluginRegistry.plugins.items()])
        args.extend(['--cache-dir', str(cache_path)])

        logger.debug(f'Installing plugins: {" ".join(args)}')
        process = run(args=args, stdout=route_output, stderr=route_output)

        if process.returncode != 0:
            logger.error(f'Plugin installation failed with error code {process.returncode}')

            if route_output == PIPE:
                logger.error(f'Plugin installation output:' + process.stdout.decode('utf-8') + process.stderr.decode('utf-8'))

        else:
            if route_output == PIPE:
                logger.debug(f'Plugin installation output:' + process.stdout.decode('utf-8') + process.stderr.decode('utf-8'))

            PluginRegistry._initialize_all_plugins()
