import unittest
import os
import shutil
import yaml

from CloudHarvestCorePluginManager.functions import list_plugins_from_github_organization, register_task_templates
from CloudHarvestCorePluginManager.registry import Registry

class TestRegisterTaskTemplates(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        from pathlib import Path
        self.test_dir = Path('./.tmp').resolve()

        # If the directory already exists, remove it
        if self.test_dir.exists():
            self.tearDown()

        self.test_dir.mkdir(parents=True, exist_ok=True)

        # Create a test directory structure with YAML files
        os.makedirs(os.path.join(self.test_dir, 'templates/reports/aws/rds'))
        os.makedirs(os.path.join(self.test_dir, 'templates/services/aws/rds'))
        os.makedirs(os.path.join(self.test_dir, 'templates/services/gcp/compute'))

        with open(os.path.join(self.test_dir, 'templates/reports/aws/rds/instances.yaml'), 'w') as f:
            yaml.dump({'key': 'aws_report_value'}, f)

        # Added to test collision of template names
        with open(os.path.join(self.test_dir, 'templates/services/aws/rds/instances.yaml'), 'w') as f:
            yaml.dump({'key': 'aws_service_value'}, f)

        with open(os.path.join(self.test_dir, 'templates/services/gcp/compute/instances.yaml'), 'w') as f:
            yaml.dump({'key': 'gcp_value'}, f)

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_register_task_templates(self):
        # Register the task templates
        register_task_templates()

        # Change the current working directory to the test directory
        os.chdir(self.test_dir)

        # Check if the templates are registered in the Registry
        aws_report_template = Registry.find(category='template_reports', name='aws.rds.instances', result_key='*')
        aws_service_template = Registry.find(category='template_services', name='aws.rds.instances', result_key='*')
        gcp_service_template = Registry.find(category='template_services', name='gcp.compute.instances', result_key='*')

        self.assertIsNotNone(aws_report_template)
        self.assertIsNotNone(gcp_service_template)
        self.assertEqual(aws_report_template, [{'category': 'template_reports', 'cls': {'key': 'aws_report_value'}, 'instances': [], 'name': 'aws.rds.instances', 'tags': []}])
        self.assertEqual(aws_service_template, [{'category': 'template_services', 'cls': {'key': 'aws_service_value'}, 'instances': [], 'name': 'aws.rds.instances', 'tags': []}])
        self.assertEqual(gcp_service_template, [{'category': 'template_services', 'cls': {'key': 'gcp_value'}, 'instances': [], 'name': 'gcp.compute.instances', 'tags': []}])


class TestFunctions(unittest.TestCase):
    def test_list_plugins_from_github_organization(self):
        # Call the function with the mocked response
        result = list_plugins_from_github_organization('Cloud-Harvest')

        # Check if the function correctly retrieves the list of repositories
        self.assertIn('CloudHarvestPluginAws', result)


if __name__ == '__main__':
    unittest.main()
