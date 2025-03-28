import sys
import traceback
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, cast
from weakref import WeakKeyDictionary, ref

from typing_extensions import Self, overload, override

P = TypeVar("P")


class _Obs(Generic[P]):
    """
    Internal holder for Property value and change listeners
    """

    __slots__ = ("value", "listeners")

    def __init__(self, value: P):
        self.value = value
        # This will keep any added listener even if it is not referenced anymore
        # and would be garbage collected
        self.listeners: set[Callable[[Any, P], Any] | Callable[[], Any]] = set()


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
        default: Optional[P] = None,
        default_factory: Optional[Callable[[Any, Any], P]] = None,
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
            obs.value = value
            self.dispatch(instance, value)

    def dispatch(self, instance, value):
        """Notifies every listener, which subscribed to the change event.

        Args:
            instance: Property instance
            value: new value to set

        """
        obs = self._get_obs(instance)
        for listener in obs.listeners:
            try:
                try:
                    # FIXME if listener() raises an error, the invalid call will be
                    #       also shown as an exception
                    listener(instance, value)  # type: ignore
                except TypeError:
                    # If the listener does not accept arguments, we call it without it
                    listener()  # type: ignore
            except Exception:
                print(
                    f"Change listener for {instance}.{self.name} = {value} raised an exception!",
                    file=sys.stderr,
                )
                traceback.print_exc()

    def bind(self, instance, callback):
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
        obs.listeners.add(callback)

    def unbind(self, instance, callback):
        """Unbinds a function from the change event of the property.

        Args:
            instance: The target instance.
            callback: The callback to unbind.
        """
        obs = self._get_obs(instance)
        obs.listeners.remove(callback)

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


def bind(instance, property: str, callback):
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

    Args:
        instance: Instance owning the property
        property: Name of the property
        callback: Function to call

    Returns:
        None
    """
    t = type(instance)
    prop = getattr(t, property)
    if isinstance(prop, Property):
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

    def dispatch(self):
        self.prop.dispatch(self.obj(), self)

    @override
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.dispatch()

    @override
    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.dispatch()

    @override
    def clear(self):
        dict.clear(self)
        self.dispatch()

    @override
    def pop(self, *args):
        result = dict.pop(self, *args)
        self.dispatch()
        return result

    @override
    def popitem(self):
        result = dict.popitem(self)
        self.dispatch()
        return result

    @override
    def setdefault(self, *args):
        dict.setdefault(self, *args)
        self.dispatch()

    @override
    def update(self, *args):
        dict.update(self, *args)
        self.dispatch()


K = TypeVar("K")
V = TypeVar("V")


class DictProperty(Property[Dict[K, V]], Generic[K, V]):
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

    def dispatch(self):
        """Dispatches the change event."""
        self.prop.dispatch(self.obj(), self)

    @override
    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.dispatch()

    @override
    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.dispatch()

    @override
    def __iadd__(self, *args):
        list.__iadd__(self, *args)
        self.dispatch()
        return self

    @override
    def __imul__(self, *args):
        list.__imul__(self, *args)
        self.dispatch()
        return self

    @override
    def append(self, *args):
        """Proxy for list.append() which dispatches the change event."""
        list.append(self, *args)
        self.dispatch()

    @override
    def clear(self):
        """Proxy for list.clear() which dispatches the change event."""
        list.clear(self)
        self.dispatch()

    @override
    def remove(self, *args):
        """Proxy for list.remove() which dispatches the change event."""
        list.remove(self, *args)
        self.dispatch()

    @override
    def insert(self, *args):
        """Proxy for list.insert() which dispatches the change event."""
        list.insert(self, *args)
        self.dispatch()

    @override
    def pop(self, *args):
        """Proxy for list.pop() which dispatches the change"""
        result = list.pop(self, *args)
        self.dispatch()
        return result

    @override
    def extend(self, *args):
        """Proxy for list.extend() which dispatches the change event."""
        list.extend(self, *args)
        self.dispatch()

    @override
    def sort(self, **kwargs):
        """Proxy for list.sort() which dispatches the change event."""
        list.sort(self, **kwargs)
        self.dispatch()

    @override
    def reverse(self):
        """Proxy for list.reverse() which dispatches the change event."""
        list.reverse(self)
        self.dispatch()


class ListProperty(Property[List[P]], Generic[P]):
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
