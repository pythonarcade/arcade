import sys
import traceback
from typing import (
    TypeVar, 
    Optional, 
    Union, 
    Callable, 
    Any, 
    Iterable, 
    Dict, 
    List, 
    Set
)
from weakref import WeakKeyDictionary, ref


class _Obs:
    """
    Internal holder for Property value and change listeners
    """

    __slots__ = "value", "listeners"

    def __init__(self) -> None:
        self.value = None
        # This will keep any added listener even if it is not referenced anymore and would be garbage collected
        self.listeners: Set[Callable] = set()


P = TypeVar("P")


class Property:
    """
    An observable property which triggers observers when changed.

    :param default: Default value which is returned, if no value set before
    :param default_factory: A callable which returns the default value.
                            Will be called with the property and the instance
    """
    __slots__ = "name", "default_factory", "obs"
    name: str

    def __init__(self, default: Any=None, default_factory: Optional[Callable]=None) -> None:
        if default_factory is None:
            default_factory = lambda prop, instance: default

        self.default_factory = default_factory
        self.obs: WeakKeyDictionary[Any: _Obs] = WeakKeyDictionary()

    def _get_obs(self, instance: Any) -> _Obs:
        obs = self.obs.get(instance)
        if obs is None:
            obs = _Obs()
            obs.value = self.default_factory(self, instance)
            self.obs[instance] = obs
        return obs

    def get(self, instance: Any) -> Any:
        obs = self._get_obs(instance)
        return obs.value

    def set(self, instance: Any, value: Any) -> None:
        obs = self._get_obs(instance)
        if obs.value != value:
            obs.value = value
            self.dispatch(instance, value)

    def dispatch(self, instance: Any, value: Any) -> None:
        obs = self._get_obs(instance)
        for listener in obs.listeners:
            try:
                listener()
            except Exception:
                print(
                    f"Change listener for {instance}.{self.name} = {value} raised an exception!",
                    file=sys.stderr,
                )
                traceback.print_exc()

    def bind(self, instance: Any, callback: Callable) -> None:
        obs = self._get_obs(instance)
        # Instance methods are bound methods, which can not be referenced by normal `ref()`
        # if listeners would be a WeakSet, we would have to add listeners as WeakMethod ourselves into `WeakSet.data`.
        obs.listeners.add(callback)

    def __set_name__(self, owner, name: str):
        self.name = name

    def __get__(self, instance: Any, owner) -> Any:
        if instance is None:
            return self
        return self.get(instance)

    def __set__(self, instance: Any, value: Any) -> None:
        self.set(instance, value)


def bind(instance, property: str, callback: Callable) -> None:
    """
    Binds a function to the change event of the property. A reference to the function will be kept,
    so that it will be still invoked, even if it would normally have been garbage collected.

        def log_change():
            print("Something changed")

        class MyObject:
            name = Property()

        my_obj = MyObject()
        bind(my_obj, "name", log_change)

        my_obj.name = "Hans"
        # > Something changed

    :param instance: Instance owning the property
    :param property: Name of the property
    :param callback: Function to call
    :return: None
    """
    t = type(instance)
    prop = getattr(t, property)
    if isinstance(prop, Property):
        prop.bind(instance, callback)


class _ObservableDict(dict):
    # Internal class to observe changes inside a native python dict.
    def __init__(self, prop: Property, instance, *largs) -> None:
        self.prop: Property = prop
        self.obj = ref(instance)
        super().__init__(*largs)

    def dispatch(self) -> None:
        self.prop.dispatch(self.obj(), self)

    def __setitem__(self, key, value) -> None:
        dict.__setitem__(self, key, value)
        self.dispatch()

    def __delitem__(self, key) -> None:
        dict.__delitem__(self, key)
        self.dispatch()

    def clear(self) -> None:
        dict.clear(self)
        self.dispatch()

    def pop(self, *largs: List):
        result = dict.pop(self, *largs)
        self.dispatch()
        return result

    def popitem(self: List):
        result = dict.popitem(self)
        self.dispatch()
        return result

    def setdefault(self, *largs: List) -> None:
        dict.setdefault(self, *largs)
        self.dispatch()

    def update(self, *largs: List) -> None:
        dict.update(self, *largs)
        self.dispatch()


class DictProperty(Property):
    """
    Property that represents a dict.
    Only dict are allowed. Any other classes are forbidden.
    """

    def __init__(self) -> None:
        super().__init__(default_factory=_ObservableDict)

    def set(self, instance: Any, value: Dict) -> None:
        value = _ObservableDict(self, instance, value)
        super().set(instance, value)


class _ObservableList(list):
    # Internal class to observe changes inside a native python list.
    def __init__(self, prop: Property, instance: Any, *largs: List) -> None:
        self.prop: Property = prop
        self.obj = ref(instance)
        super().__init__(*largs)

    def dispatch(self) -> None:
        self.prop.dispatch(self.obj(), self)

    def __setitem__(self, key: Any, value: List) -> None:
        list.__setitem__(self, key, value)
        self.dispatch()

    def __delitem__(self, key: Any) -> None:
        list.__delitem__(self, key)
        self.dispatch()

    def __iadd__(self, *largs: List) -> _ObservableList:  # type: ignore
        list.__iadd__(self, *largs)
        self.dispatch()
        return self

    def __imul__(self, *largs: List) -> _ObservableList:  # type: ignore
        list.__imul__(self, *largs)
        self.dispatch()
        return self

    def append(self, *largs: List) -> None:
        list.append(self, *largs)
        self.dispatch()

    def clear(self) -> None:
        list.clear(self)
        self.dispatch()

    def remove(self, *largs: List) -> None:
        list.remove(self, *largs)
        self.dispatch()

    def insert(self, *largs: List) -> None:
        list.insert(self, *largs)
        self.dispatch()

    def pop(self, *largs: List) -> None:
        result = list.pop(self, *largs)
        self.dispatch()
        return result

    def extend(self, *largs: Iterable[Any, ...]) -> None:
        list.extend(self, *largs)
        self.dispatch()

    def sort(self, **kwargs: Dict) -> None:
        list.sort(self, **kwargs)
        self.dispatch()

    def reverse(self) -> None:
        list.reverse(self)
        self.dispatch()


class ListProperty(Property):
    """
    Property that represents a list.
    Only list are allowed. Any other classes are forbidden.
    """

    def __init__(self) -> None:
        super().__init__(default_factory=_ObservableList)

    def set(self, instance: Any, value: Dict) -> None:
        value = _ObservableList(self, instance, value)  # type: ignore
        super().set(instance, value)
