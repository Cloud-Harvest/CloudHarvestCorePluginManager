import unittest
from CloudHarvestCorePluginManager import register_definition
from CloudHarvestCorePluginManager import Registry


class TestDecorators(unittest.TestCase):
    def setUp(self):
        # Clear the Registry before each test
        Registry.clear()

    def test_register_definition(self):
        @register_definition(name='test_class_name', category='task', register_instances=True)
        class TestClass:
            def __init__(self, *args, **kwargs):
                pass

        registered_name = 'task-test_class_name'

        # Check if the class was added to the Registry's definitions
        self.assertIn(registered_name, Registry._OBJECTS.keys())
        self.assertEqual(Registry._OBJECTS[registered_name]['category'], 'task')
        self.assertEqual(Registry._OBJECTS[registered_name]['cls'], TestClass)
        self.assertEqual(Registry.find(result_key='cls', name='test_class_name', category='task'), [TestClass])

        test_class = TestClass()
        self.assertEqual(test_class, Registry._OBJECTS[registered_name]['instances'][0])
        self.assertIn(test_class, Registry.find(result_key='instances', name='test_class_name', category='task'))

        @register_definition(name='test_class_name2', category='task', register_instances=True)
        class TestClass2:
            def __init__(self, *args, **kwargs):
                pass

        registered_name_2 = 'task-test_class_name2'

        # Check if the class was added to the Registry's definitions
        self.assertIn(registered_name_2, Registry._OBJECTS.keys())
        self.assertEqual(Registry._OBJECTS[registered_name_2]['category'], 'task')
        self.assertEqual(Registry._OBJECTS[registered_name_2]['cls'], TestClass2)
        self.assertEqual(Registry.find(result_key='cls', name='test_class_name2', category='task'), [TestClass2])

        test_class2A = TestClass2()
        test_class2B = TestClass2()
        test_class2C = TestClass2()

        self.assertEqual(3, len(Registry._OBJECTS[registered_name_2]['instances']))
        self.assertIn(test_class2A, Registry._OBJECTS[registered_name_2]['instances'])
        self.assertIn(test_class2B, Registry._OBJECTS[registered_name_2]['instances'])
        self.assertIn(test_class2C, Registry._OBJECTS[registered_name_2]['instances'])

        self.assertEqual(1, len(Registry.find(result_key='instances', name='test_class_name', category='task')))

        # Test that the class metadata was added
        self.assertTrue(hasattr(TestClass, '_harvest_plugin_metadata'))

        from json import load
        with open('../meta.json') as metadata_file:
            metadata = load(metadata_file)

        self.assertEqual(getattr(test_class, '_harvest_plugin_metadata'), metadata)

if __name__ == '__main__':
    unittest.main()
