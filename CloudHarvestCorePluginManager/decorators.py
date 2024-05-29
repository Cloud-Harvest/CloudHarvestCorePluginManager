from .registry import Registry


def register_definition(cls):
    """
    A decorator to register a class in the 'Registry.definitions' when defined.

    The most common scenario for needing this decorator involes Tasks. This way, a Task can be found when planning a
    TaskChain.

    Example:
    >>> @register_definition
    >>> class MyClass:
    >>>     pass
    """

    # Add the class to the Registry
    Registry.definitions[cls.__name__] = cls

    # Return the class
    return cls


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
