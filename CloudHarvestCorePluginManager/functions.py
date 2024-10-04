from typing import List
from logging import getLogger

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
