import unittest
import os
import shutil
import tempfile
import yaml

from CloudHarvestCorePluginManager.functions import list_plugins_from_github_organization, find_task_templates, register_task_templates
from CloudHarvestCorePluginManager.registry import Registry

class TestRegisterTaskTemplates(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Create a test directory structure with YAML files
        os.makedirs(os.path.join(self.test_dir, 'templates/reports/aws/rds'))
        os.makedirs(os.path.join(self.test_dir, 'templates/services/gcp/compute'))

        with open(os.path.join(self.test_dir, 'templates/reports/aws/rds/instances.yaml'), 'w') as f:
            yaml.dump({'key': 'aws_value'}, f)

        with open(os.path.join(self.test_dir, 'templates/services/gcp/compute/instances.yaml'), 'w') as f:
            yaml.dump({'key': 'gcp_value'}, f)

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_find_task_templates(self):
        # Change the current working directory to the test directory
        os.chdir(self.test_dir)

        # Call the function
        result = find_task_templates()

        # Expected result
        expected_result = {
            'aws.rds.instances': {
                'tags': 'reports',
                'template': {'key': 'aws_value'}
            },
            'gcp.compute.instances': {
                'tags': 'services',
                'template': {'key': 'gcp_value'}
            }
        }

        # Check if the result matches the expected result
        self.assertEqual(result, expected_result)

        self.find_result = result

    def test_register_task_templates(self):
        # Change the current working directory to the test directory
        os.chdir(self.test_dir)

        # Find task templates
        templates_dict = find_task_templates()

        # Register task templates
        register_task_templates(templates_dict)

        # Check if the templates are registered in the Registry
        aws_template = Registry.find(category='template', name='aws.rds.instances', tags=['reports'], result_key='*')
        gcp_template = Registry.find(category='template', name='gcp.compute.instances', tags=['services'], result_key='*')

        self.assertIsNotNone(aws_template)
        self.assertIsNotNone(gcp_template)
        self.assertEqual(aws_template, [{'category': 'template', 'cls': {'key': 'aws_value'}, 'instances': [], 'name': 'aws.rds.instances', 'tags': 'reports'}])
        self.assertEqual(gcp_template, [{'category': 'template', 'cls': {'key': 'gcp_value'}, 'instances': [], 'name': 'gcp.compute.instances', 'tags': 'services'}])


class TestFunctions(unittest.TestCase):
    def test_list_plugins_from_github_organization(self):
        # Call the function with the mocked response
        result = list_plugins_from_github_organization('Cloud-Harvest')

        # Check if the function correctly retrieves the list of repositories
        self.assertIn('CloudHarvestPluginAws', result)


if __name__ == '__main__':
    unittest.main()
