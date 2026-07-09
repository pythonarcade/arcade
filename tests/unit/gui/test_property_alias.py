import gc

import pytest

from arcade.gui.property import AliasProperty, Property, bind, unbind
from .test_property import Observer


class ChildWithProperty:
    """A simple child object with a Property."""

    text = Property("")
    value = Property(0)


class ParentWithAlias:
    """Parent exposes child's properties via AliasProperty."""

    def __init__(self):
        self._child = ChildWithProperty()

    # String shorthand for child_getter
    text = AliasProperty("_child", "text")
    # Callable form for child_getter
    value = AliasProperty(lambda self: self._child, "value")


def test_alias_property_get_string_shorthand():
    """Test basic get with string shorthand child_getter."""
    parent = ParentWithAlias()
    parent._child.text = "hello"
    assert parent.text == "hello"


def test_alias_property_set_string_shorthand():
    """Test basic set with string shorthand child_getter."""
    parent = ParentWithAlias()
    parent.text = "world"
    assert parent._child.text == "world"
    assert parent.text == "world"


def test_alias_property_get_callable():
    """Test basic get with callable child_getter."""
    parent = ParentWithAlias()
    parent._child.value = 42
    assert parent.value == 42


def test_alias_property_set_callable():
    """Test basic set with callable child_getter."""
    parent = ParentWithAlias()
    parent.value = 100
    assert parent._child.value == 100
    assert parent.value == 100


def test_alias_property_bind_receives_parent():
    """Listeners bound to alias should receive the parent as instance."""
    observer = Observer()
    parent = ParentWithAlias()

    bind(parent, "text", observer.call_with_instance_value)
    parent.text = "changed"

    assert observer.called
    assert observer.call_args[0] is parent  # First arg is parent, not child
    assert observer.call_args[1] == "changed"


def test_alias_property_unbind():
    """Unbind should remove listener from the alias."""
    observer = Observer()
    parent = ParentWithAlias()

    bind(parent, "text", observer)
    parent.text = "one"
    assert observer.count == 1

    unbind(parent, "text", observer)
    parent.text = "two"
    # Count should not increase
    assert observer.count == 1


def test_alias_property_no_arg_listener():
    """Test listener with no arguments."""
    parent = ParentWithAlias()
    called = []

    def callback():
        called.append(True)

    bind(parent, "text", callback)
    parent.text = "fire"
    assert called == [True]


def test_alias_property_instance_listener():
    """Test listener that receives only the instance."""
    parent = ParentWithAlias()
    received_instances = []

    def callback(instance):
        received_instances.append(instance)

    bind(parent, "text", callback)
    parent.text = "hello"
    assert received_instances == [parent]


def test_alias_property_instance_value_listener():
    """Test listener with (instance, value) signature."""
    observer = Observer()
    parent = ParentWithAlias()

    bind(parent, "text", observer.call_with_instance_value)
    parent.text = "test"

    assert observer.called
    assert observer.call_args == (parent, "test")


def test_alias_property_instance_new_old_listener():
    """Test listener with (instance, value, old_value) signature."""
    observer = Observer()
    parent = ParentWithAlias()
    parent._child.text = "old"

    bind(parent, "text", observer.call_with_instance_value_old)
    parent.text = "new"

    assert observer.called
    assert observer.call_args == (parent, "new", "old")


def test_alias_property_multiple_listeners():
    """Test multiple listeners on the same alias property."""
    parent = ParentWithAlias()
    observer1 = Observer()
    observer2 = Observer()

    bind(parent, "text", observer1)
    bind(parent, "text", observer2)

    parent.text = "both"

    assert observer1.called
    assert observer2.called


def test_alias_property_gc_parent():
    """Test garbage collection of parent allows cleanup."""
    parent = ParentWithAlias()
    observer = Observer()

    bind(parent, "text", observer)
    parent.text = "before"
    assert observer.count == 1

    # Parent is deleted; WeakRef in forwarder closure allows GC
    del parent
    gc.collect()

    # Can't directly verify parent is gone, but no exception should occur


def test_alias_property_directed_write():
    """Test that direct write to child is also visible via alias."""
    parent = ParentWithAlias()
    parent._child.text = "direct"
    assert parent.text == "direct"


def test_alias_property_multiple_aliases_same_child():
    """Test multiple alias properties on same child's different properties."""
    parent = ParentWithAlias()

    parent.text = "foo"
    parent.value = 99

    assert parent._child.text == "foo"
    assert parent._child.value == 99


def test_alias_property_invalid_child_property():
    """Test error when child has the attribute but it's not a Property."""

    class ChildWithNonProperty:
        text = "not a property"  # Regular attribute, not a Property

    class BadParent:
        def __init__(self):
            self._child = ChildWithNonProperty()

        text = AliasProperty("_child", "text")

    parent = BadParent()

    # Error only occurs when trying to bind (which checks _child_prop)
    with pytest.raises(ValueError, match="is not an arcade.gui.Property"):
        bind(parent, "text", lambda: None)


def test_alias_property_bind_multiple_times_same_callback():
    """Test binding the same callback twice (should proxy twice)."""
    parent = ParentWithAlias()
    observer = Observer()

    bind(parent, "text", observer)
    bind(parent, "text", observer)

    # Both proxies are registered, so callback fires twice
    parent.text = "twice"
    assert observer.count == 2


def test_alias_property_equality_check():
    """Test that setting to same value doesn't trigger listeners."""
    parent = ParentWithAlias()
    observer = Observer()

    parent.text = "initial"
    bind(parent, "text", observer)

    # Set to same value
    parent.text = "initial"
    # Child's Property.set() has equality guard, so dispatch doesn't fire
    assert observer.count == 0

    # Set to different value
    parent.text = "different"
    assert observer.count == 1


def test_alias_property_with_weak_bind():
    """Test weak binding on alias (should not cause lifecycle issues)."""

    class MyHolder:
        def __init__(self):
            self._child = ChildWithProperty()

        text = AliasProperty("_child", "text")

        def on_text_change(self, instance, value):
            self.last_value = value

    holder = MyHolder()
    bind(holder, "text", holder.on_text_change, weak=True)

    holder.text = "changed"
    assert holder.last_value == "changed"


def test_alias_property_child_replacement():
    """Test that alias continues to work if child is replaced."""
    parent = ParentWithAlias()

    parent.text = "original"
    assert parent.text == "original"

    # Replace child
    parent._child = ChildWithProperty()
    parent._child.text = "new_child"

    # Alias should now read from new child
    assert parent.text == "new_child"

    # And write to new child
    parent.text = "updated"
    assert parent._child.text == "updated"


def test_alias_property_listener_not_called_after_child_replacement():
    """Test that listeners remain bound to original child, not new child.

    When a child is replaced, previously-bound listeners don't automatically
    migrate to the new child. This is expected—listeners are tied to the
    specific child instance they were bound to.
    """
    parent = ParentWithAlias()
    observer = Observer()

    bind(parent, "text", observer.call_with_instance_value)
    parent.text = "first"
    assert observer.count == 1

    # Replace child — listener is now bound to the old child
    original_child = parent._child
    parent._child = ChildWithProperty()

    # Write through alias — fires on NEW child, not old
    parent.text = "second"
    # Listener was bound to original_child, so it doesn't fire
    assert observer.count == 1

    # But the old child's property still has the listener
    original_child.text = "third"  # Directly set
    assert observer.count == 2  # This should fire


def test_alias_property_rebind_after_child_replacement():
    """Test that you can rebind listeners after replacing child."""
    parent = ParentWithAlias()
    observer = Observer()

    bind(parent, "text", observer.call_with_instance_value)
    parent.text = "first"
    assert observer.count == 1

    # Replace child
    parent._child = ChildWithProperty()

    # Rebind listener to the new setup
    unbind(parent, "text", observer.call_with_instance_value)
    bind(parent, "text", observer.call_with_instance_value)

    # Now listener fires on new child
    parent.text = "second"
    assert observer.count == 2
    assert observer.call_args[1] == "second"
