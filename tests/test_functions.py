import unittest
from CloudHarvestCorePluginManager.functions import list_plugins_from_github_organization


class TestFunctions(unittest.TestCase):
    def test_list_plugins_from_github_organization(self):
        # Call the function with the mocked response
        result = list_plugins_from_github_organization('Cloud-Harvest')

        # Check if the function correctly retrieves the list of repositories
        self.assertIn('CloudHarvestPluginAws', result)


if __name__ == '__main__':
    unittest.main()
