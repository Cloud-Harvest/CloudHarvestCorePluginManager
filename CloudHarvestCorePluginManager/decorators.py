from .registry import Registry


def register_definition(name: str):
    """
    A decorator to register a class in the 'Registry.definitions' when defined.

    The decorator takes the `name` argument. The `name` arugment is used when searching for classes using the
    Registery.find_definition() method.

    The most common scenario for needing this decorator involves Tasks. This way, a Task can be found when planning a
    TaskChain.

    Args:
        name (str, optional): The name to use as the key in the `Registry.definitions` dictionary.
                              If not provided, the class's name is used.

    Example:
    >>> @register_definition(name='MyNamedClass')
    >>> class MyClass:
    >>>     pass
    """

    def decorator(cls):
        # Add the class to the Registry
        Registry.definitions[name] = cls

        # Return the class
        return cls

    return decorator


def register_instance(cls):
    """
    A decorator to register an instance in the 'Registry.instances' when its class is instantiated.

    The most common scenario for this decorator is registering Flask Blueprints for the API.

    >>> @register_instance
    >>> class MyClass:
    >>>     pass
    """

    # Save the original __init__ method
    original_init = cls.__init__

    # Define a new __init__ method
    def new_init(self, *args, **kwargs):
        # Call the original __init__ method
        original_init(self, *args, **kwargs)

        # Register the instance if it does not already exist in the list
        if self not in Registry.instances:
            Registry.instances.append(self)

    # Replace the class's __init__ method with the new one
    cls.__init__ = new_init

    # Return the class
    return cls
