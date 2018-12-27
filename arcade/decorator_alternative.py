import arcade

__all__ = ["override", "decorator_run"]

_registry = {}


class ArcadeContextError(AssertionError):
    """An error raised when override functions are called outside the context of an arcade.Window object."""
    pass


def _bind(window: arcade.Window):
    """Overrides the stored functions from the registry into the arcade.Window object.
    Args:
        window: The window object whose functions we want to override.
    """
    for method_name, func in _registry.items():
        setattr(window, method_name, func)


def override(func):
    """Registers override functions for later binding with the _bind function.
    Called as a decorator.

    Args:
        func (function): The function that will be stored into _registry
            to eventually override the arcade.Window object method of the
            same name.

    Returns (function): An 'empty' function that, if called outside the context
            of an arcade.Window object, will raise an error.
    """
    method_name = func.__name__
    if not callable(getattr(arcade.Window, method_name)):
        raise AttributeError(f"Window attribute '{method_name}' is not callable.")

    _registry[method_name] = func

    def empty_function():
        raise ArcadeContextError(f"The function '{method_name}' should not be called "
                                 "outside the context of an arcade.Window object.")
    return empty_function


def decorator_run(width=800,
                  height=600,
                  title="Arcade Window",
                  full_screen=False,
                  resizable=False,
                  background_color=arcade.color.BLACK):
    """Creates an instance of an arcade.Window, binds override functions, and runs arcade."""
    window = arcade.Window(width, height, title, full_screen, resizable)
    _bind(window)

    # need to reset the update function pointers after binding
    window.set_update_rate(1/80)

    arcade.set_background_color(background_color)
    arcade.run()



