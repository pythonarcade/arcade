import gc
from typing import Dict

from arcade.gui.property import bind, DictProperty, _ObservableDict
from .test_property import Observer


def test_dict_property_gc():
    class MyDictHolder:
        data = DictProperty()

    obj = MyDictHolder()
    obj.data = {}

    # Keeps referenced objects
    gc.collect()
    assert len(MyDictHolder.data.obs) == 1

    # delete ref and trigger gc
    del obj
    gc.collect()

    # No left overs
    assert len(MyDictHolder.data.obs) == 0


def test_dict_property_replace_dict_with_observable():
    class MyDictHolder:
        data = DictProperty()

    obj = MyDictHolder()
    obj.data = {}

    assert isinstance(obj.data, _ObservableDict)


def test_dict_property_set():
    class MyDictHolder:
        data = DictProperty()

    observer = Observer()
    obj = MyDictHolder()
    bind(obj, "data", observer)

    obj.data["test"] = 5

    assert observer.called


def test_dict_property_del():
    class MyDictHolder:
        data = DictProperty()

    obj = MyDictHolder()
    obj.data["test"] = 5

    observer = Observer()
    bind(obj, "data", observer)

    del obj.data["test"]

    assert observer.called


def test_dict_property_clear():
    class MyDictHolder:
        data: Dict = DictProperty()

    obj = MyDictHolder()
    observer = Observer()
    bind(obj, "data", observer)

    obj.data.clear()

    assert observer.called


def test_dict_property_pop():
    class MyDictHolder:
        data: Dict = DictProperty()

    obj = MyDictHolder()
    obj.data["test"] = 5

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.pop("test")

    assert observer.called


def test_dict_property_pop_item():
    class MyDictHolder:
        data: Dict = DictProperty()

    obj = MyDictHolder()
    obj.data["test"] = 5

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.popitem()

    assert observer.called


def test_dict_property_set_default():
    class MyDictHolder:
        data: Dict = DictProperty()

    obj = MyDictHolder()
    obj.data["test"] = 5

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.setdefault("test", 5)

    assert observer.called


def test_dict_property_update():
    class MyDictHolder:
        data: Dict = DictProperty()

    obj = MyDictHolder()
    obj.data["test"] = 5

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.update({"test": 5})

    assert observer.called
