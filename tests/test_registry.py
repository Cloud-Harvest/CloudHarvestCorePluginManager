import unittest
from CloudHarvestCorePluginManager.registry import Registry
from CloudHarvestCorePluginManager.decorators import register_definition


class TestRegistry(unittest.TestCase):
    def setUp(self):
        # Clear the Registry before each test
        Registry.clear()

    def test_find_definition(self):
        @register_definition(name='test_class', category='task', register_instances=True)
        class TestClass:
            pass

        # Add a class to the Registry's definitions
        Registry.add(category='task', name='test_class', cls=TestClass)

        # Test find with the configuration name
        result = Registry.find(result_key='name', name='test_class')[0]
        self.assertEqual(result, 'test_class')

        # Test find with the class name
        result = Registry.find(result_key='cls', name='test_class')[0]
        self.assertEqual(result, TestClass)

        # Test find with the category
        result = Registry.find(result_key='category', category='task')[0]
        self.assertEqual(result, 'task')

        test_instance = TestClass()
        self.assertIn(test_instance, Registry.find(result_key='instances', name='test_class'))

        @register_definition(name='test_class2', category='task')
        class UnregisteredClass:
            pass

        # Test find with an unregistered class
        self.assertIn(UnregisteredClass, Registry.find(result_key='cls', name='test_class2'))

        unregistered_class = UnregisteredClass()
        self.assertEqual([], Registry.find(result_key='instances', name='test_class2'))

        # Test tags
        @register_definition(name='test_class3', category='task', tags=['tag1', 'tag2'])
        class TaggedClass:
            pass

        self.assertIn(TaggedClass, Registry.find(result_key='cls', tags=['tag1']))
        self.assertIn(TaggedClass, Registry.find(result_key='cls', tags=['tag2']))
        self.assertIn(TaggedClass, Registry.find(result_key='cls', tags=['tag1', 'tag2']))
        self.assertEqual([], Registry.find(result_key='cls', tags=['tag3']))

class TestRegisterTaskTemplates(unittest.TestCase):
    def setUp(self):
        import os
        import yaml

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
        import shutil
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_register_task_templates(self):
        import os
        from CloudHarvestCorePluginManager.registry import register_task_templates

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


if __name__ == '__main__':
    unittest.main()