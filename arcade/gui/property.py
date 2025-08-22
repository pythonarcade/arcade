import inspect
import sys
import traceback
import warnings
import weakref
from collections.abc import Callable
from contextlib import contextmanager, suppress
from enum import Enum
from inspect import ismethod
from typing import Any, Generic, TypeVar, cast
from weakref import WeakKeyDictionary, ref

from typing_extensions import Self, overload, override

P = TypeVar("P")


NoArgListener = Callable[[], None]
InstanceListener = Callable[[Any], None]
InstanceValueListener = Callable[[Any, Any], None]
InstanceNewOldListener = Callable[[Any, Any, Any], None]
AnyListener = NoArgListener | InstanceListener | InstanceValueListener | InstanceNewOldListener


class _ListenerType(Enum):
    """Enum to represent the type of listener"""

    NO_ARG = 0
    INSTANCE = 1
    INSTANCE_VALUE = 2
    INSTANCE_NEW_OLD = 3

    @staticmethod
    def detect_callback_type(callback: AnyListener) -> "_ListenerType":
        """Normalizes the callback so every callback can be invoked with the same signature."""
        signature = inspect.signature(callback)

        # first detect the old *args default listener signatures
        with suppress(TypeError):
            signature.bind(..., ...)
            return _ListenerType.INSTANCE_VALUE

        # check for the most common signature
        with suppress(TypeError):
            signature.bind()
            return _ListenerType.NO_ARG

        # check for the other
        with suppress(TypeError):
            signature.bind(..., ..., ...)
            return _ListenerType.INSTANCE_NEW_OLD

        with suppress(TypeError):
            signature.bind(...)
            return _ListenerType.INSTANCE

        raise TypeError("Callback is not callable")


class _Obs(Generic[P]):
    """
    Internal holder for Property value and change listeners
    """

    __slots__ = ("value", "_listeners")

    def __init__(self, value: P):
        self.value = value
        # This will keep any added listener even if it is not referenced anymore
        # and would be garbage collected
        self._listeners: dict[AnyListener, _ListenerType] = dict()

    def add(
        self,
        callback: AnyListener,
    ):
        """Add a callback to the list of listeners"""
        self._listeners[callback] = _ListenerType.detect_callback_type(callback)

    def remove(self, callback):
        """Remove a callback from the list of listeners"""
        if callback in self._listeners:
            del self._listeners[callback]

    @property
    def listeners(self) -> list[tuple[AnyListener, _ListenerType]]:
        """Returns a list of all listeners and type, both weak and strong."""
        # todo returning a iterator would be more efficient, but might also break
        # improve ~0.01 sec
        return list(self._listeners.items())


class Property(Generic[P]):
    """An observable property which triggers observers when changed.

    .. code-block:: python

        def log_change(instance, value):
            print("Something changed")

        class MyObject:
            name = Property()

        my_obj = MyObject()
        bind(my_obj, "name", log_change)
        unbind(my_obj, "name", log_change)

        my_obj.name = "Hans"
        # > Something changed

    Properties provide a less verbose way to implement the observer pattern in comparison to
    using the `property` decorator.

    Args:
        default: Default value which is returned, if no value set before
        default_factory: A callable which returns the default value.
            Will be called with the property and the instance
    """

    __slots__ = ("name", "default_factory", "obs")
    name: str
    """Attribute name of the property"""
    default_factory: Callable[[Any, Any], P]
    """Default factory to create the initial value"""
    obs: WeakKeyDictionary[Any, _Obs]
    """Weak dictionary to hold the value and listeners"""

    def __init__(
        self,
        default: P | None = None,
        default_factory: Callable[[Any, Any], P] | None = None,
    ):
        if default_factory is None:
            default_factory = lambda prop, instance: cast(P, default)

        self.default_factory = default_factory
        self.obs: WeakKeyDictionary[Any, _Obs] = WeakKeyDictionary()

    def _get_obs(self, instance) -> _Obs:
        obs = self.obs.get(instance)
        if obs is None:
            obs = _Obs(self.default_factory(self, instance))
            self.obs[instance] = obs
        return obs

    def get(self, instance) -> P:
        """Get value for owner instance"""
        obs = self._get_obs(instance)
        return obs.value

    def set(self, instance, value):
        """Set value for owner instance"""
        obs = self._get_obs(instance)
        if obs.value != value:
            old = obs.value
            obs.value = value
            self.dispatch(instance, value, old)

    def dispatch(self, instance, value, old_value):
        """Notifies every listener, which subscribed to the change event.

        Args:
            instance: Property instance
            value: new value set
            old_value: previous value

        """
        obs = self._get_obs(instance)
        for listener, _listener_type in obs.listeners:
            try:
                if _listener_type == _ListenerType.NO_ARG:
                    listener()  # type: ignore[call-arg]
                elif _listener_type == _ListenerType.INSTANCE:
                    listener(instance)  # type: ignore[call-arg]
                elif _listener_type == _ListenerType.INSTANCE_VALUE:
                    listener(instance, value)  # type: ignore[call-arg]
                elif _listener_type == _ListenerType.INSTANCE_NEW_OLD:
                    listener(instance, value, old_value)  # type: ignore[call-arg]
            except Exception:
                print(
                    f"Change listener for {instance}.{self.name} = {value} raised an exception!",
                    file=sys.stderr,
                )
                traceback.print_exc()

    def bind(self, instance: Any, callback: AnyListener):
        """Binds a function to the change event of the property.

        A reference to the function will be kept.

        Args:
             instance: The instance to bind the callback to.
             callback: The callback to bind.
        """
        obs = self._get_obs(instance)
        # Instance methods are bound methods, which can not be referenced by normal `ref()`
        # if listeners would be a WeakSet, we would have to add listeners as WeakMethod
        # ourselves into `WeakSet.data`.
        obs.add(callback)

    def unbind(self, instance, callback):
        """Unbinds a function from the change event of the property.

        Args:
            instance: The target instance.
            callback: The callback to unbind.
        """
        obs = self._get_obs(instance)
        obs.remove(callback)

    def __set_name__(self, owner, name):
        self.name = name

    @overload
    def __get__(self, instance: None, instance_type) -> Self: ...

    @overload
    def __get__(self, instance: Any, instance_type) -> P: ...

    def __get__(self, instance: Any | None, instance_type) -> Self | P:
        if instance is None:
            return self
        return self.get(instance)

    def __set__(self, instance, value: P):
        self.set(instance, value)


class _WeakCallback:
    """Wrapper for weakly referencing a callback function.

    Which allows to bind methods of the instance itself without
    causing memory leaks.

    Also supports to be stored in a dict or set, because it implements
    __hash__ and __eq__ methods to match the original function.
    """

    def __init__(self, func):
        self._func_type = _ListenerType.detect_callback_type(func)  # type: ignore[assignment]
        self._hash = hash(func)

        if inspect.ismethod(func):
            self._func = weakref.WeakMethod(func)
        else:
            self._func = weakref.ref(func)

    def __call__(self, instance, new_value, old_value):
        func = self._func()
        if func is None:
            warnings.warn("WeakCallable was called without a callable object.")

        if self._func_type == _ListenerType.NO_ARG:
            return func()
        elif self._func_type == _ListenerType.INSTANCE:
            return func(instance)
        elif self._func_type == _ListenerType.INSTANCE_VALUE:
            return func(instance, new_value)
        elif self._func_type == _ListenerType.INSTANCE_NEW_OLD:
            return func(instance, new_value, old_value)

        else:
            raise TypeError(f"Unsupported callback type: {self._func_type}")

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if ismethod(other):
            return self._hash == hash(other)
        return False


def bind(instance, property: str, callback: AnyListener, weak=False):
    """Bind a function to the change event of the property.

    A reference to the function will be kept, so that it will be still
    invoked even if it would normally have been garbage collected:

    .. code-block:: python

        def log_change(instance, value):
            print(f"Value of {instance} changed to {value}")

        class MyObject:
            name = Property()

        my_obj = MyObject()
        bind(my_obj, "name", log_change)

        my_obj.name = "Hans"
        # > Value of <__main__.MyObject ...> changed to Hans

    Binding to a method of the Property owner itself can cause a memory leak, because the
    owner is strongly referenced. Instead, bind the class method, which will be invoked with
    the instance as first parameter. `bind(instance, "property_name", Instance.method)`.
    Or use the `weak` parameter to bind the method weakly
    bind(instance, "property_name", instance.method, weak=True)`.

    Args:
        instance: Instance owning the property
        property: Name of the property
        callback: Function to call
        weak: If True, the callback will be weakly referenced.
            This is useful for methods of the instance itself to avoid memory leaks.

    Returns:
        None
    """

    if weak:
        # If weak is True, we use a _WeakCallable to avoid strong references
        callback = _WeakCallback(callback)  # type: ignore[assignment]

    # TODO rename property to property_name for arcade 4.0 (just to be sure)
    t = type(instance)
    prop = getattr(t, property)
    if not isinstance(prop, Property):
        raise ValueError(f"{t.__name__}.{property} is not an arcade.gui.Property")

    prop.bind(instance, callback)


def unbind(instance, property: str, callback):
    """Unbinds a function from the change event of the property.

    .. code-block:: python

        def log_change(instance, value):
            print("Something changed")

        class MyObject:
            name = Property()

        my_obj = MyObject()
        bind(my_obj, "name", log_change)
        unbind(my_obj, "name", log_change)

        my_obj.name = "Hans"
        # > Something changed

    Args:
        instance: Instance owning the property
        property: Name of the property
        callback: Function to unbind

    Returns:
        None
    """
    t = type(instance)
    prop = getattr(t, property)
    if isinstance(prop, Property):
        prop.unbind(instance, callback)


class _ObservableDict(dict):
    """Internal class to observe changes inside a native python dict."""

    __slots__ = ("prop", "obj")

    def __init__(self, prop: Property, instance, *args):
        self.prop: Property = prop
        self.obj = ref(instance)
        super().__init__(*args)

    @contextmanager
    def _dispatch(self):
        """This is a context manager which will dispatch the change event
        when the context is exited.
        """
        old_value = self.copy()
        yield
        self.prop.dispatch(self.obj(), self, old_value)

    @override
    def __setitem__(self, key, value):
        with self._dispatch():
            dict.__setitem__(self, key, value)

    @override
    def __delitem__(self, key):
        with self._dispatch():
            dict.__delitem__(self, key)

    @override
    def clear(self):
        with self._dispatch():
            dict.clear(self)

    @override
    def pop(self, *args):
        with self._dispatch():
            return dict.pop(self, *args)

    @override
    def popitem(self):
        with self._dispatch():
            return dict.popitem(self)

    @override
    def setdefault(self, *args):
        with self._dispatch():
            return dict.setdefault(self, *args)

    @override
    def update(self, *args):
        with self._dispatch():
            dict.update(self, *args)


K = TypeVar("K")
V = TypeVar("V")


class DictProperty(Property[dict[K, V]], Generic[K, V]):
    """Property that represents a dict.

    Only dict are allowed. Any other classes are forbidden.
    """

    def __init__(self):
        super().__init__(default_factory=_ObservableDict)

    @override
    def set(self, instance, value: dict):
        """Set value for owner instance, wraps the dict into an observable dict."""
        value = _ObservableDict(self, instance, value)
        super().set(instance, value)


class _ObservableList(list):
    """Internal class to observe changes inside a native python list.

    Args:
        prop: Property instance
        instance: Instance owning the property
        *args: List of arguments to pass to the list
    """

    __slots__ = ("prop", "obj")

    def __init__(self, prop: Property, instance, *args):
        self.prop: Property = prop
        self.obj = ref(instance)
        super().__init__(*args)

    @contextmanager
    def _dispatch(self):
        """Dispatches the change event.
        This is a context manager which will dispatch the change event
        when the context is exited.
        """
        old_value = self.copy()
        yield
        self.prop.dispatch(self.obj(), self, old_value)

    @override
    def __setitem__(self, key, value):
        with self._dispatch():
            list.__setitem__(self, key, value)

    @override
    def __delitem__(self, key):
        with self._dispatch():
            list.__delitem__(self, key)

    @override
    def __iadd__(self, *args):
        with self._dispatch():
            list.__iadd__(self, *args)
        return self

    @override
    def __imul__(self, *args):
        with self._dispatch():
            list.__imul__(self, *args)
        return self

    @override
    def append(self, *args):
        """Proxy for list.append() which dispatches the change event."""
        with self._dispatch():
            list.append(self, *args)

    @override
    def clear(self):
        """Proxy for list.clear() which dispatches the change event."""
        with self._dispatch():
            list.clear(self)

    @override
    def remove(self, *args):
        """Proxy for list.remove() which dispatches the change event."""
        with self._dispatch():
            list.remove(self, *args)

    @override
    def insert(self, *args):
        """Proxy for list.insert() which dispatches the change event."""
        with self._dispatch():
            list.insert(self, *args)

    @override
    def pop(self, *args):
        """Proxy for list.pop() which dispatches the change"""
        with self._dispatch():
            result = list.pop(self, *args)
        return result

    @override
    def extend(self, *args):
        """Proxy for list.extend() which dispatches the change event."""
        with self._dispatch():
            list.extend(self, *args)

    @override
    def sort(self, **kwargs):
        """Proxy for list.sort() which dispatches the change event."""
        with self._dispatch():
            list.sort(self, **kwargs)

    @override
    def reverse(self):
        """Proxy for list.reverse() which dispatches the change event."""
        with self._dispatch():
            list.reverse(self)


class ListProperty(Property[list[P]], Generic[P]):
    """Property that represents a list.

    Only list are allowed. Any other classes are forbidden.
    """

    def __init__(self):
        super().__init__(default_factory=_ObservableList)

    @override
    def set(self, instance, value: list):
        """Set value for owner instance, wraps the list into an observable list."""
        value = _ObservableList(self, instance, value)
        super().set(instance, value)
