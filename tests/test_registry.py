import unittest
from unittest.mock import patch
from registry import PluginRegistry


class DummyClass:
    pass


class TestPluginRegistry(unittest.TestCase):
    def setUp(self):

        PluginRegistry.classes = {
            'package1': {'Class1': str, 'Class2': int},
            'package2': {'Class3': str, 'Class4': int},
            'package3': {'Class5': DummyClass, 'Class6': bool},
        }

    def test_find_classes(self):
        # Test finding a class that exists
        result = PluginRegistry.find_classes('Class1', 'package1')
        self.assertTrue(isinstance(result, str.__class__))

        result = PluginRegistry.find_classes('Class5')
        self.assertTrue(isinstance(result, DummyClass.__class__))

        # Test finding a class that doesn't exist
        result = PluginRegistry.find_classes('Class3', 'package1')
        self.assertIsNone(result)

        # Test finding a class with is_instance_of parameter
        result = PluginRegistry.find_classes('Class1', 'package1', is_instance_of=str.__class__)
        self.assertTrue(isinstance(result, str.__class__))

        # Test finding a class with is_subclass_of parameter
        result = PluginRegistry.find_classes('Class1', 'package1', is_subclass_of=object)
        self.assertTrue(isinstance(result, str.__class__))

        # Test finding a class with return_all_matching parameter
        result = PluginRegistry.find_classes('Class1', 'package1', return_all_matching=True)
        self.assertTrue(all(isinstance(cls, str.__class__) for cls in result))


if __name__ == '__main__':
    unittest.main()
