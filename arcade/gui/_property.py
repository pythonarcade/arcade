import warnings
from _weakrefset import WeakSet
from weakref import WeakKeyDictionary


class _Obs:
    """
    Internal holder for Property value and change lsiteners
    """
    __slots__ = 'value', 'listeners'

    def __init__(self):
        self.value = None
        self.listeners = WeakSet()


class _Property:
    """
    An observable property which triggers observers when changed.
    """
    __slots__ = "name", "default", "obs"

    name: str

    def __init__(self, default=None):
        self.default = default
        self.obs = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self

        obs = self._get_obs(instance)
        return obs.value

    def __set_name__(self, owner, name):
        self.name = name

    def _get_obs(self, instance) -> _Obs:
        obs = self.obs.get(instance)
        if obs is None:
            obs = _Obs()
            self.obs[instance] = obs
        return obs

    def __set__(self, instance, value):
        obs = self._get_obs(instance)
        obs.value = value
        for listener in obs.listeners:
            try:
                listener()
            except:
                warnings.warn(f"Change listener for {instance}.{self.name} = {value} raised an exception!")

    def bind(self, instance, callback):
        self._get_obs(instance).listeners.add(callback)


def _bind(instance, property, callback):
    """
    Binds a function to the change event of the property.

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


# class ObservableList(list):
#     # Internal class to observe changes inside a native python list.
#     def __init__(self, *largs):
#         self.prop = largs[0]
#         self.obj = ref(largs[1])
#         self.last_op = '', None
#         super(ObservableList, self).__init__(*largs[2:])
#
#     def __setitem__(self, key, value):
#         list.__setitem__(self, key, value)
#         self.last_op = '__setitem__', key
#         observable_list_dispatch(self)
#
#     def __delitem__(self, key):
#         list.__delitem__(self, key)
#         self.last_op = '__delitem__', key
#         observable_list_dispatch(self)
#
#     def __setslice__(self, b, c, v):
#         list.__setslice__(self, b, c, v)
#         self.last_op = '__setslice__', (b, c)
#         observable_list_dispatch(self)
#
#     def __delslice__(self, b, c):
#         list.__delslice__(self, b, c)
#         self.last_op = '__delslice__', (b, c)
#         observable_list_dispatch(self)
#
#     def __iadd__(self, *largs):
#         list.__iadd__(self, *largs)
#         self.last_op = '__iadd__', None
#         observable_list_dispatch(self)
#
#     def __imul__(self, b):
#         list.__imul__(self, b)
#         self.last_op = '__imul__'. b
#         observable_list_dispatch(self)
#
#     def append(self, *largs):
#         list.append(self, *largs)
#         self.last_op = 'append', None
#         observable_list_dispatch(self)
#
#     def remove(self, *largs):
#         list.remove(self, *largs)
#         self.last_op = 'remove', None
#         observable_list_dispatch(self)
#
#     def insert(self, i, x):
#         list.insert(self, i, x)
#         self.last_op = 'insert', i
#         observable_list_dispatch(self)
#
#     def pop(self, *largs):
#         cdef object result = list.pop(self, *largs)
#         self.last_op = 'pop', largs
#         observable_list_dispatch(self)
#         return result
#
#     def extend(self, *largs):
#         list.extend(self, *largs)
#         self.last_op = 'extend', None
#         observable_list_dispatch(self)
#
#     def sort(self, *largs, **kwargs):
#         list.sort(self, *largs, **kwargs)
#         self.last_op = 'sort', None
#         observable_list_dispatch(self)
#
#     def reverse(self, *largs):
#         list.reverse(self, *largs)
#         self.last_op = 'reverse', None
#         observable_list_dispatch(self)