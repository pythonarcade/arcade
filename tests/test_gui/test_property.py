import gc
from typing import Dict

from arcade.gui._property import _Property, _bind, _DictProperty, _ObservableDict


class MyObject:
    name = _Property()


class Observer:
    called = None

    def __call__(self, *args, **kwargs):
        self.called = (args, kwargs)


def test_callback():
    observer = Observer()

    class MyObject:
        name = _Property()

    my_obj = MyObject()
    _bind(my_obj, "name", observer)

    assert not observer.called

    # WHEN
    my_obj.name = "New Name"

    assert observer.called == (tuple(), {})


def test_get_default():
    my_obj = MyObject()
    assert my_obj.name is None


def test_set_and_get_value():
    my_obj = MyObject()

    # WHEN
    my_obj.name = "New Name"

    assert my_obj.name == "New Name"


def test_independent_obj_instances():
    my_obj1 = MyObject()
    my_obj2 = MyObject()

    # WHEN
    my_obj1.name = "Hans"
    my_obj2.name = "Franz"

    assert my_obj1.name == "Hans"
    assert my_obj2.name == "Franz"


def test_gc_entries_are_collected():
    obj = MyObject()
    obj.name = "Some Name"

    # Keeps referenced objects
    gc.collect()
    assert len(MyObject.name.obs) == 1

    # delete ref and trigger gc
    del obj
    gc.collect()

    # No left overs
    assert len(MyObject.name.obs) == 0
