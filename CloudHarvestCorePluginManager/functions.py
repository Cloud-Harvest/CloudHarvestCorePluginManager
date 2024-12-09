from enum import unique
from typing import Dict, List
from logging import getLogger
from unicodedata import category

logger = getLogger('harvest')


def list_plugins_from_github_organization(organization: str) -> List[str]:
    """
    Retrieves the names of all repositories in the specified GitHub organization.

    Args:
        organization (str): The name of the GitHub organization.

    Returns:
        A list of repository names in the specified GitHub organization.
    """

    from requests import get
    from json import loads

    url = f'https://api.github.com/orgs/{organization}/repos'
    response = get(url)

    if response.status_code == 200:
        return [
            repo['name'] for repo in loads(response.text)
            if 'CloudHarvestPlugin' in repo['name']
        ]

    return []

def register_all():
    """
    Executes all methods in this file that start with 'register_' (except for this method).
    """

    import inspect

    for name, method in inspect.getmembers(globals()):
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
                        unique_name = '.'.join(
                            os.path.relpath(file_path, directory).split(os.sep)[1:-1] + [os.path.splitext(file)[0]]
                        )

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
    from .registry import Registry
    for template_name, template_data in templates_dict.items():
        # Ensure the template name is valid
        if len(template_name.split('.')) < 3:
            logger.warning(f'Invalid template name: {template_name}. Templates must be in a subdirectory of the `template` directory. This defines the kind of template (e.g. report, service, task). Skipping...')

        # The first position in the template name is the category, and the rest is the registration name
        template_category = template_name.split('.')[1]
        template_registration_name = '.'.join(template_name.split('.')[2:])

        Registry.add(name=template_registration_name,
                     category=f'template_{template_category}',
                     cls=template_data)
