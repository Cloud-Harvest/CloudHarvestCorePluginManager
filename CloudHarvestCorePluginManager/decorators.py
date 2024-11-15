from os.path import expanduser, abspath

from .registry import Registry
from logging import getLogger

logger = getLogger('harvest')


def register_definition(category: str, name: str, register_instances: bool = False):
    """
    A decorator to register a class in the Registry when it is defined.

    :param category: The category of the class. Lowercase is enforced.
    :param name: The name of the class. Lowercase is enforced.
    :param register_instances: If True, automatically register instances of the class. It is not necessary to register
    instances unless the application must later retrieve them, such as CommandSet (CLI) or Blueprint (API) instances.

    Example
    >>> @register_definition(category='task', name='my_task', register_instances=True)
    >>> class MyTask:
    >>>     pass
    """

    def decorator(cls):
        """
        A decorator to register a class in the Registry when it is defined.
        :param cls: A class
        :return: The class
        """

        # Get the class's module metadata
        metadata = get_class_module_metadata(cls)
        setattr(cls, '_harvest_plugin_metadata', metadata)

        # Add the class to the Registry
        Registry.add(name=name, category=category, cls=cls)

        if register_instances:
            original_init = cls.__init__

            def new_init(self, *args, **kwargs):
                # Call the original __init__ method
                original_init(self, *args, **kwargs)

                # Add the instance to the Registry
                Registry.add(name=name, instances=[self])

            # Replace the class's __init__ method with the new one
            cls.__init__ = new_init

        # Return the class
        return cls

    return decorator

def get_class_module_metadata(cls) -> dict:
    # Here we'll read the module's metadata and store it for future reference
    from os.path import abspath, expanduser, join, sep
    from inspect import getmodule
    module = getmodule(cls)

    new_path = []
    from re import compile
    for part in abspath(expanduser(module.__file__)).split(sep):
        # Skip empty parts
        if part == '':
            continue

        new_path.append(part)

        # We only want to include the module path up to the root module directory where we can find the meta.json file
        # This regex expression will match the root module directory, but not the root development directory
        # commonly named 'CloudHarvest'.
        if compile('CloudHarvest.').match(part):
            break

    module_path = join('/', *new_path)
    module_name = new_path[-1]

    try:
        meta_path = join(module_path, 'meta.json')
        import json
        with open(join(meta_path), 'r') as metadata_file:
            return json.load(metadata_file)

    except FileNotFoundError:
        logger.error(f"Metadata file not found for class {cls.__name__} in module {module_name}")
