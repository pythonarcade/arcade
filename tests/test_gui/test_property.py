import gc

from arcade.gui.property import Property, bind


class MyObject:
    name = Property()


class Observer:
    called = None

    def call(self, *args, **kwargs):
        self.called = (args, kwargs)

    def __call__(self, *args, **kwargs):
        self.called = (args, kwargs)


def test_callback():
    observer = Observer()

    my_obj = MyObject()
    bind(my_obj, "name", observer)

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


def test_does_not_trigger_if_value_unchanged():
    observer = Observer()
    my_obj = MyObject()
    my_obj.name = "CONSTANT"
    bind(my_obj, "name", observer)

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

    # No left overs
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
