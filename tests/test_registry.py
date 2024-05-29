import unittest
from CloudHarvestCorePluginManager.registry import Registry


class TestRegistry(unittest.TestCase):
    def setUp(self):
        # Clear the Registry before each test
        Registry.definitions = {}
        Registry.instances = []

    def test_find_definition(self):
        class TestClass:
            pass

        # Add a class to the Registry's definitions
        Registry.definitions['TestClass'] = TestClass

        # Test find_definition with the class name
        result = Registry.find_definition('TestClass', None, None, False)
        self.assertEqual(result, [TestClass])

        # Test find_definition with is_instance_of
        result = Registry.find_definition(None, type, None, False)
        self.assertEqual(result, [TestClass])

        # Test find_definition with is_subclass_of
        result = Registry.find_definition(None, None, object, False)
        self.assertEqual(result, [TestClass])

    def test_find_instance(self):
        class TestClass:
            pass

        # Create an instance of the class and add it to the Registry's instances
        instance = TestClass()
        Registry.instances.append(instance)

        # Test find_instance with the class name
        result = Registry.find_instance('TestClass', None, None, False)
        self.assertEqual(result, [instance])

        # Test find_instance with is_instance_of
        result = Registry.find_instance(None, TestClass, None, False)
        self.assertEqual(result, [instance])

        # Test find_instance with is_subclass_of
        result = Registry.find_instance(None, None, object, False)
        self.assertEqual(result, [instance])


if __name__ == '__main__':
    unittest.main()