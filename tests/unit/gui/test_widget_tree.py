import gc

from arcade.gui import UIEvent, UIWidget
from arcade.gui.widgets import UIDummy


def test_widget_add_child():
    # GIVEN
    parent = UIDummy()
    child = UIDummy()

    # WHEN
    parent.add(child)

    # THEN
    assert child in parent.children


def test_widget_add_child_at_index_0():
    # GIVEN
    parent = UIDummy()
    child_1 = UIDummy()
    child_2 = UIDummy()

    # WHEN
    parent.add(child_1)
    parent.add(child_2, index=0)

    # THEN
    children = parent.children
    assert children[0] == child_2
    assert children[1] == child_1


def test_widget_remove_child():
    # GIVEN
    parent = UIDummy()
    child = UIDummy()

    # WHEN
    parent.add(child)
    parent.remove(child)

    # THEN
    assert child not in parent.children


def test_widget_remove_child_returns_kwargs():
    # GIVEN
    parent = UIDummy()
    child = UIDummy()

    # WHEN
    parent.add(child, key="value")
    kwargs = parent.remove(child)

    # THEN
    assert kwargs == {"key": "value"}


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


def test_chained_widgets_are_collected_by_gc():
    """
    Test that chained widgets are collected by garbage collector.
    This is to ensure that there are no memory leaks when widgets are
    added and removed in a chain.
    """

    def objs_in_memory(obj_type):
        """Check if an object of a specific type is in memory."""
        return len([obj for obj in gc.get_objects() if isinstance(obj, obj_type)])

    gc.collect()
    start_count = objs_in_memory(UIWidget)

    root = UIWidget()
    root.add(UIWidget())

    # children are not collected until the parent is deleted
    gc.collect()
    assert objs_in_memory(UIWidget) == start_count + 2

    del root
    gc.collect()

    # This might help, if the test fails ;)
    # requires `objgraph`
    # if objs_in_memory(UIWidget) > start_count:
    # print("Render object graph...")
    # import objgraph
    #
    # objgraph.show_chain(
    #     objgraph.find_backref_chain(
    #         [obj for obj in gc.get_objects() if isinstance(obj, UIWidget)][1],
    #         objgraph.is_proper_module,
    #     ),
    #     # filename="chain.png",
    # )

    # print("Render backrefs...")
    # objgraph.show_backrefs(
    #     [[obj for obj in gc.get_objects() if isinstance(obj, UIWidget)][1]],
    #     max_depth=15,
    #     # filename="sample-graph.png",
    # )

    assert objs_in_memory(UIWidget) == start_count
