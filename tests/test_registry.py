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

if __name__ == '__main__':
    unittest.main()