import unittest
from CloudHarvestCorePluginManager.decorators import register_definition, register_instance
from CloudHarvestCorePluginManager.registry import Registry


class TestDecorators(unittest.TestCase):
    def setUp(self):
        # Clear the Registry before each test
        Registry.definitions = {}
        Registry.instances = []

    def test_register_definition(self):
        @register_definition
        class TestClass:
            pass

        # Check if the class was added to the Registry's definitions
        self.assertIn('TestClass', Registry.definitions)
        self.assertEqual(Registry.definitions['TestClass'], TestClass)

    def test_register_instance(self):
        @register_instance
        class TestClass:
            pass

        # Create an instance of the class
        instance = TestClass()

        # Check if the instance was added to the Registry's instances
        self.assertIn(instance, Registry.instances)


if __name__ == '__main__':
    unittest.main()
