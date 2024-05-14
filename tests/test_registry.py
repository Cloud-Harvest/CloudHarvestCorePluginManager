import unittest
from CloudHarvestCorePluginManager.registry import PluginRegistry


class TestPluginRegistry(unittest.TestCase):
    def setUp(self):
        from dummy.test import DummyClass

        PluginRegistry.plugins = {
            'https://github.com/Cloud-Harvest/CloudHarvestPluginAws.git': 'main'
        }

        PluginRegistry.classes = {
            'package1': {'Class1': str, 'Class2': int},
            'package2': {'Class3': str, 'Class4': int},
            'package3': {'Class5': DummyClass, 'Class6': bool},
        }

        from importlib import import_module
        self.dummy_module = import_module('tests.dummy')

        # Reset the instantiated_classes dictionary
        PluginRegistry.instantiated_classes = {}

    def test_install(self):
        # Test installing plugins
        PluginRegistry.install(quiet=False)
        [
            self.assertTrue(expected_plugin in PluginRegistry.classes.keys())
            for expected_plugin in ['CloudHarvestPluginAws', 'CloudHarvestCoreTasks', 'CloudHarvestCoreDataModel']
        ]

    def test_find_classes(self):
        from dummy.test import DummyClass

        # Test finding a class that exists
        result = PluginRegistry.find_classes(class_name='Class1', package_name='package1', return_type='classes')
        self.assertTrue(isinstance(result, str.__class__))

        result = PluginRegistry.find_classes(class_name='Class5', return_type='classes')
        self.assertTrue(isinstance(result, DummyClass.__class__))

        # Test finding a class that doesn't exist
        result = PluginRegistry.find_classes(class_name='ClassDerp', package_name='package1', return_type='classes')
        self.assertIsNone(result)

        # Test finding a class with is_instance_of parameter
        result = PluginRegistry.find_classes(class_name='Class1', package_name='package1', is_instance_of=str.__class__, return_type='classes')
        self.assertTrue(isinstance(result, str.__class__))

        # Test finding a class with is_subclass_of parameter
        result = PluginRegistry.find_classes(class_name='Class1', package_name='package1', is_subclass_of=object, return_type='classes')
        self.assertTrue(isinstance(result, str.__class__))

        # Test finding a class with return_all_matching parameter
        result = PluginRegistry.find_classes(class_name='Class1', package_name='package1', return_all_matching=True, return_type='classes')
        self.assertTrue(all(isinstance(cls, str.__class__) for cls in result))

        # Register an instantiated class (dummy.test.DummyClass) as dummy_instantiated
        PluginRegistry.register_instantiated_classes_by_path('.')

        # Test finding an instantiated class
        from dummy.test import DummyClass
        result = PluginRegistry.find_classes(class_name='DummyClass', package_name='tests', return_type='instantiated')
        self.assertTrue(isinstance(result, DummyClass))

        # Test finding both classes and instantiated classes
        PluginRegistry.classes['tests'] = {'DummyClass': DummyClass}
        result = PluginRegistry.find_classes(class_name='DummyClass', return_type='both')
        self.assertTrue(len(result) == 2)
        self.assertTrue(any(isinstance(cls, DummyClass) for cls in result))
        self.assertTrue(any(type(cls) is DummyClass) for cls in result)

    def test_register_instantiated_classes(self):
        from dummy.test import DummyClass

        # Call the method with the dummy module
        PluginRegistry.register_instantiated_classes_by_path('dummy')

        # Check if the DummyClass was registered
        result = PluginRegistry.instantiated_classes['dummy']['dummy.test'][0]
        self.assertEqual(result.name, 'dummy')

        self.assertTrue(isinstance(result, DummyClass))

        # check from relative path '.'
        PluginRegistry.instantiated_classes = {}
        PluginRegistry.register_instantiated_classes_by_path('.')

        # Check if the DummyClass was registered
        result = PluginRegistry.instantiated_classes['tests']['dummy.test'][0]
        self.assertEqual(result.name, 'dummy')

        from dummy.test import DummyClass
        self.assertTrue(isinstance(result, DummyClass))



if __name__ == '__main__':
    unittest.main()
