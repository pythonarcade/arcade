from arcade.gui import UIEvent
from arcade.gui.widgets import UIDummy


def test_widget_add_child():
    # GIVEN
    parent = UIDummy()
    child = UIDummy()

    # WHEN
    parent.add(child)

    # THEN
    assert child in parent.children


def test_widget_remove_child():
    # GIVEN
    parent = UIDummy()
    child = UIDummy()

    # WHEN
    parent.add(child)
    parent.remove(child)

    # THEN
    assert child not in parent.children


def test_widget_clear_children():
    # GIVEN
    parent = UIDummy()
    child = UIDummy()

    # WHEN
    parent.add(child)
    parent.clear()

    # THEN
    assert child not in parent.children


def test_widget_events_passed_to_children():
    # GIVEN
    parent = UIDummy()
    child = UIDummy()

    triggered = False

    @child.event
    def on_event(event):
        nonlocal triggered
        triggered = True

    # WHEN
    parent.add(child)
    parent.dispatch_ui_event(UIEvent(None))

    # THEN
    assert triggered is True


def test_iterate_widget_children(window):
    # GIVEN
    parent = UIDummy()
    child1 = UIDummy()
    child2 = UIDummy()
    child3 = UIDummy()

    # WHEN
    parent.add(child1)
    parent.add(child2)
    child2.add(child3)

    # THEN
    assert list(parent) == [child1, child2]
