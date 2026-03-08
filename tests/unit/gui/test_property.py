import gc

import pytest

from arcade.gui.property import Property, bind, unbind


class MyObject:
    name = Property()


class Observer:
    call_args = None
    called = False
    count = 0

    def call(self):
        self.call_args = tuple()
        self.called = True
        self.count += 1

    def call_with_instance(self, instance):
        """Match expected signature of 2 parameters"""
        self.call_args = (instance,)
        self.called = True
        self.count += 1

    def call_with_instance_value(self, instance, value):
        """Match expected signature of 2 parameters"""
        self.call_args = (instance, value)
        self.called = True
        self.count += 1

    def call_with_instance_value_old(self, instance, value, old):
        """Match expected signature of 2 parameters"""
        self.call_args = (instance, value, old)
        self.called = True
        self.count += 1

    def call_with_args(self, *args):
        self.call_args = args
        self.called = True
        self.count += 1

    def __call__(self, *args, **kwargs):
        self.call_args = args
        self.called = True
        self.count += 1


def test_bind_callback():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call)

    assert not observer.call_args

    # WHEN
    my_obj.name = "New Name"

    assert observer.call_args == tuple()


def test_bind_callback_only_once():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call)
    bind(my_obj, "name", observer.call)

    assert not observer.call_args

    # WHEN
    my_obj.name = "New Name"

    assert observer.call_args == tuple()
    assert observer.count == 1


def test_bind_callback_accepts_instance():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call_with_instance)

    assert not observer.call_args

    # WHEN
    my_obj.name = "New Name"

    assert observer.call_args == (my_obj,)

    # Remove reference of call_args to my_obj, otherwise it will keep the object alive
    observer.call_args = None


def test_bind_callback_accepts_instance_value():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call_with_instance_value)

    assert not observer.call_args

    # WHEN
    my_obj.name = "New Name"

    assert observer.call_args == (my_obj, "New Name")

    # Remove reference of call_args to my_obj, otherwise it will keep the object alive
    observer.call_args = None


def test_bind_callback_accepts_instance_value_old():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call_with_instance_value_old)

    assert not observer.call_args

    # WHEN
    my_obj.name = "New Name"

    assert observer.call_args == (my_obj, "New Name", None)

    # Remove reference of call_args to my_obj, otherwise it will keep the object alive
    observer.call_args = None


def test_bind_callback_with_star_args():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call_with_args)

    # WHEN
    my_obj.name = "New Name"

    assert observer.call_args == (my_obj, "New Name")

    # Remove reference of call_args to my_obj, otherwise it will keep the object alive
    observer.call_args = None


def test_unbind_function_callback():
    called = False

    def callback(*args):
        nonlocal called
        called = True

    my_obj = MyObject()
    bind(my_obj, "name", callback)

    # WHEN
    unbind(my_obj, "name", callback)
    my_obj.name = "New Name"

    assert not called


def test_unbind_method_callback():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call)

    gc.collect()

    # WHEN
    unbind(my_obj, "name", observer.call)
    my_obj.name = "New Name"

    assert not observer.called


def test_unbind_weak_method_callback():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call, weak=True)

    gc.collect()

    # WHEN
    unbind(my_obj, "name", observer.call)
    my_obj.name = "New Name"

    assert not observer.called


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


def test_does_not_trigger_if_value_unchanged():
    observer = Observer()
    my_obj = MyObject()
    my_obj.name = "CONSTANT"
    bind(my_obj, "name", observer.call)

    assert not observer.called

    # WHEN
    my_obj.name = "CONSTANT"

    assert not observer.called


def test_gc_entries_are_collected():
    obj = MyObject()
    obj.name = "Some Name"

    # Keeps referenced objects
    gc.collect()
    assert len(MyObject.name.obs) == 1

    # delete ref and trigger gc
    del obj
    gc.collect()

    # No leftovers
    assert len(MyObject.name.obs) == 0


def test_obj_collected_when_using_class_method():
    class ObserverAndObject(Observer, MyObject):
        pass

    obj = ObserverAndObject()
    bind(obj, "name", ObserverAndObject.call)

    # Keeps referenced objects
    gc.collect()
    assert len(MyObject.name.obs) == 1

    # delete ref and trigger gc
    del obj
    gc.collect()

    # No leftovers
    assert len(MyObject.name.obs) == 0


def test_gc_bound_methods_strongly_referenced():
    class ObserverAndObject(Observer, MyObject):
        pass

    obj = ObserverAndObject()
    bind(obj, "name", obj.call)

    # Keeps referenced objects
    gc.collect()
    assert len(ObserverAndObject.name.obs) == 1

    # delete ref and trigger gc
    del obj
    gc.collect()

    # No leftovers
    assert len(ObserverAndObject.name.obs) == 1


def test_gc_keeps_bound_methods():
    observer = Observer()
    obj = MyObject()
    obj.name = "Some Name"

    bind(obj, "name", observer.call)

    assert len(MyObject.name.obs[obj]._listeners) == 1

    del observer
    gc.collect()

    assert len(MyObject.name.obs[obj]._listeners) == 1


def test_gc_keeps_temp_methods():
    obj = MyObject()
    obj.name = "Some Name"
    calls = []

    def callback(*args, **kwargs):
        calls.append((args, kwargs))

    bind(obj, "name", callback)

    assert len(MyObject.name.obs[obj]._listeners) == 1

    del callback

    assert len(MyObject.name.obs[obj]._listeners) == 1


def test_bind_raise_if_attr_not_a_ui_property():
    class BadObject:
        @property
        def name(self):
            return

    obj = BadObject()

    with pytest.raises(ValueError):
        bind(obj, "name", lambda *args: None)
