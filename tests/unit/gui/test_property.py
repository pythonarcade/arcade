import gc

from arcade.gui.property import Property, bind, unbind


class MyObject:
    name = Property()


class Observer:
    call_args = None
    called = False

    def call(self):
        self.call_args = tuple()
        self.called = True

    def call_with_args(self, instance, value):
        """Match expected signature of 2 parameters"""
        self.call_args = (instance, value)
        self.called = True

    def __call__(self, *args):
        self.call_args = args
        self.called = True


def test_bind_callback():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call)

    assert not observer.call_args

    # WHEN
    my_obj.name = "New Name"

    assert observer.call_args == tuple()


def test_bind_callback_with_args():
    """
    A bound callback can have 0 or 2 arguments.
    0 arguments are used for simple callbacks, like `log_change`.
    2 arguments are used for callbacks that need to know the instance and the new value.
    """
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call_with_args)

    assert not observer.call_args

    # WHEN
    my_obj.name = "New Name"

    assert observer.call_args == (my_obj, "New Name")

    # Remove reference of call_args to my_obj, otherwise it will keep the object alive
    observer.call_args = None


def test_bind_callback_with_star_args():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer)

    # WHEN
    my_obj.name = "New Name"

    assert observer.call_args == (my_obj, "New Name")

    # Remove reference of call_args to my_obj, otherwise it will keep the object alive
    observer.call_args = None


def test_unbind_callback():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer.call)

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


def test_gc_keeps_bound_methods():
    observer = Observer()
    obj = MyObject()
    obj.name = "Some Name"

    bind(obj, "name", observer.call)

    assert len(MyObject.name.obs[obj].listeners) == 1

    del observer
    gc.collect()

    assert len(MyObject.name.obs[obj].listeners) == 1


def test_gc_keeps_temp_methods():
    obj = MyObject()
    obj.name = "Some Name"
    calls = []

    def callback(*args, **kwargs):
        calls.append((args, kwargs))

    bind(obj, "name", callback)

    assert len(MyObject.name.obs[obj].listeners) == 1

    del callback

    assert len(MyObject.name.obs[obj].listeners) == 1
