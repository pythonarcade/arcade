import gc
from typing import List

from arcade.gui.property import bind, ListProperty, _ObservableList
from .test_property import Observer


class MyListHolder:
    data: List = ListProperty()


def test_list_property_gc():
    obj = MyListHolder()
    obj.data = {}

    # Keeps referenced objects
    gc.collect()
    assert len(MyListHolder.data.obs) == 1

    # delete ref and trigger gc
    del obj
    gc.collect()

    # No left overs
    assert len(MyListHolder.data.obs) == 0


def test_list_property_replace_list_with_observable():
    obj = MyListHolder()
    obj.data = []

    assert isinstance(obj.data, _ObservableList)


def test_list_property_set():
    observer = Observer()
    obj = MyListHolder()
    obj.data.append(1)

    bind(obj, "data", observer)
    obj.data[0] = 5

    assert observer.called


def test_list_property_del():
    obj = MyListHolder()
    obj.data.append(1)

    observer = Observer()
    bind(obj, "data", observer)

    del obj.data[0]

    assert observer.called


def test_list_property_clear():
    obj = MyListHolder()
    observer = Observer()
    bind(obj, "data", observer)

    obj.data.clear()

    assert observer.called


def test_list_property_pop():
    obj = MyListHolder()
    obj.data.append(1)

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.pop()

    assert observer.called


def test_list_property_sort():
    obj = MyListHolder()
    obj.data.append(1)

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.sort()

    assert observer.called


def test_list_property_update():
    obj = MyListHolder()
    obj.data.append(1)

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.extend([2])

    assert observer.called


def test_list_property_insert():
    obj = MyListHolder()
    obj.data.append(1)

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.insert(0, 2)

    assert observer.called


def test_list_property_reverse():
    obj = MyListHolder()
    obj.data.append(1)

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.reverse()

    assert observer.called


def test_list_property_remove():
    obj = MyListHolder()
    obj.data.append(1)

    observer = Observer()
    bind(obj, "data", observer)

    obj.data.remove(1)

    assert observer.called


def test_list_property_imul():
    obj = MyListHolder()
    obj.data.append(1)

    observer = Observer()
    bind(obj, "data", observer)

    obj.data *= 2

    assert observer.called


def test_list_property_iadd():
    obj = MyListHolder()
    obj.data.append(1)

    observer = Observer()
    bind(obj, "data", observer)

    obj.data += [2]

    assert observer.called
