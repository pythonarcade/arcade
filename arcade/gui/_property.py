import warnings
from weakref import WeakKeyDictionary, ref


class _Obs:
    """
    Internal holder for Property value and change listeners
    """
    __slots__ = 'value', 'listeners'

    def __init__(self):
        self.value = None
        # This will keep any added listener even if it is not referenced anymore and would be garbage collected
        self.listeners = set()


class _Property:
    """
    An observable property which triggers observers when changed.
    """
    __slots__ = "name", "default_factory", "obs"

    name: str

    def __init__(self, default=None, default_factory=None):
        """

        :type default: Default value which is returned, if no value set before
        """
        if default_factory is None:
            default_factory = lambda prop, instance: default

        self.default_factory = default_factory
        self.obs = WeakKeyDictionary()

    def _get_obs(self, instance) -> _Obs:
        obs = self.obs.get(instance)
        if obs is None:
            obs = _Obs()
            obs.value = self.default_factory(self, instance)
            self.obs[instance] = obs
        return obs

    def get(self, instance):
        obs = self._get_obs(instance)
        return obs.value

    def set(self, instance, value):
        obs = self._get_obs(instance)
        if obs.value != value:
            obs.value = value
            self.dispatch(instance, value)

    def dispatch(self, instance, value):
        obs = self._get_obs(instance)
        for listener in obs.listeners:
            try:
                listener()
            except Exception:
                warnings.warn(f"Change listener for {instance}.{self.name} = {value} raised an exception!")

    def bind(self, instance, callback):
        obs = self._get_obs(instance)
        # Instance methods are bound methods, which can not be referenced by normal `ref()`
        # if listeners would be a WeakSet, we would have to add listeners as WeakMethod ourselves into `WeakSet.data`.
        obs.listeners.add(callback)

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.get(instance)

    def __set__(self, instance, value):
        self.set(instance, value)


def _bind(instance, property: str, callback):
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
    if isinstance(prop, _Property):
        prop.bind(instance, callback)


class _ObservableDict(dict):
    # Internal class to observe changes inside a native python dict.
    def __init__(self, prop: _Property, instance, *largs):
        self.prop: _Property = prop
        self.obj = ref(instance)
        super().__init__(*largs)

    def dispatch(self):
        self.prop.dispatch(self.obj(), self)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.dispatch()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.dispatch()

    def clear(self):
        dict.clear(self)
        self.dispatch()

    def pop(self, *largs):
        result = dict.pop(self, *largs)
        self.dispatch()
        return result

    def popitem(self):
        result = dict.popitem(self)
        self.dispatch()
        return result

    def setdefault(self, *largs):
        dict.setdefault(self, *largs)
        self.dispatch()

    def update(self, *largs):
        dict.update(self, *largs)
        self.dispatch()


class _DictProperty(_Property):
    """
    Property that represents a dict.
    Only dict are allowed. Any other classes are forbidden.
    """

    def __init__(self):
        super().__init__(default_factory=_ObservableDict)

    def set(self, instance, value: dict):
        value = _ObservableDict(self, instance, value)
        super().set(instance, value)


class _ObservableList(list):
    # Internal class to observe changes inside a native python list.
    def __init__(self, prop: _Property, instance, *largs):
        self.prop: _Property = prop
        self.obj = ref(instance)
        super().__init__(*largs)

    def dispatch(self):
        self.prop.dispatch(self.obj(), self)

    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.dispatch()

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.dispatch()

    def __iadd__(self, *largs):  # type: ignore
        list.__iadd__(self, *largs)
        self.dispatch()
        return self

    def __imul__(self, *largs):  # type: ignore
        list.__imul__(self, *largs)
        self.dispatch()
        return self

    def append(self, *largs):
        list.append(self, *largs)
        self.dispatch()

    def clear(self):
        list.clear(self)
        self.dispatch()

    def remove(self, *largs):
        list.remove(self, *largs)
        self.dispatch()

    def insert(self, *largs):
        list.insert(self, *largs)
        self.dispatch()

    def pop(self, *largs):
        result = list.pop(self, *largs)
        self.dispatch()
        return result

    def extend(self, *largs):
        list.extend(self, *largs)
        self.dispatch()

    def sort(self, **kwargs):
        list.sort(self, **kwargs)
        self.dispatch()

    def reverse(self):
        list.reverse(self)
        self.dispatch()


class _ListProperty(_Property):
    """
    Property that represents a list.
    Only list are allowed. Any other classes are forbidden.
    """

    def __init__(self):
        super().__init__(default_factory=_ObservableList)

    def set(self, instance, value: dict):
        value = _ObservableList(self, instance, value)  # type: ignore
        super().set(instance, value)
