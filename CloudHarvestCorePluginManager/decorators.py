from .registry import Registry


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
