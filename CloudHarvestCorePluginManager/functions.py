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

