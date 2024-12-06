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


def register_task_templates(templates_dict: Dict[str, Dict]) -> None:
    """
    Registers task templates in the Registry.

    Args:
        templates_dict (Dict[str, Dict]): A dictionary of unique names (keys) and the contents of the files (values).
    """
    from CloudHarvestCorePluginManager.registry import Registry

    for template_name, template_configuration in templates_dict.items():
        Registry.add(name=template_name,
                     category='template',
                     cls=template_configuration['template'],
                     tags=template_configuration['tags'])


def find_task_templates() -> Dict[str, Dict]:
    """
    Scans the current project and all site packages for a `templates` directory, finds all nested YAML files,
    constructs unique names for the objects, and returns a dictionary of unique names and the contents of the files
    loaded using the YAML FullLoader.

    Returns:
        A dictionary of unique names (keys) and the contents of the files (values).
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

                        template_tags = unique_name.split('.')[0]
                        template_name = '.'.join(unique_name.split('.')[1:])

                        if templates_dict.get(unique_name):
                            logger.debug(f'Found duplicate template: {unique_name}')
                            continue

                        with open(file_path, 'r') as yaml_file:
                            templates_dict[template_name] = {
                                'template': yaml.load(yaml_file, Loader=yaml.FullLoader),
                                'tags': template_tags
                            }

    # Scan the current project directory
    scan_directory(os.getcwd())

    # Scan the site-packages directories
    for site_packages_path in site.getsitepackages():
        for root, dirs, _ in os.walk(site_packages_path):
            for dir_name in dirs:
                if dir_name.startswith('CloudHarvest'):
                    scan_directory(os.path.join(root, dir_name))

    return templates_dict