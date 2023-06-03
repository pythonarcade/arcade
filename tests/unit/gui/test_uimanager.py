from arcade.gui import UIManager, UIDummy


def test_walk_widgets(window):
    manager = UIManager()
    widget1 = UIDummy()
    manager.add(widget1)

    children = list(child for child in manager.walk_widgets())

    assert children == [widget1]


def test_walk_widgets_of_specific_layer(window):
    manager = UIManager()
    widget1 = UIDummy()
    widget2 = UIDummy()
    manager.add(widget1)
    manager.add(widget2, layer=1)

    children = list(child for child in manager.walk_widgets(layer=1))

    assert children == [widget2]


def test_walk_widgets_of_all_layers(window):
    manager = UIManager()
    widget1 = UIDummy()
    widget2 = UIDummy()
    manager.add(widget1)
    manager.add(widget2, layer=1)

    children = list(child for child in manager.walk_widgets(layer=None))

    assert children == [widget2, widget1]


def test_walk_widgets_down_the_tree(window):
    manager = UIManager()
    widget1 = UIDummy()
    widget2 = UIDummy()
    widget1.add(widget2)
    manager.add(widget1)

    children = list(manager.walk_widgets())

    assert children == [widget2, widget1]


def test_get_widgets_at(window):
    manager = UIManager()
    widget1 = UIDummy(x=50, y=50, width=100, height=100)
    widget2 = UIDummy(x=75, y=75, width=50, height=50)
    widget1.add(widget2)
    manager.add(widget1)

    children = list(manager.get_widgets_at(pos=(100, 100)))
    assert children == [widget2, widget1]

    children = list(manager.get_widgets_at(pos=(60, 60)))
    assert children == [widget1]


def test_get_widgets_at_from_layer_0_by_default(window):
    manager = UIManager()
    widget1 = UIDummy(x=50, y=50, width=100, height=100)
    widget2 = UIDummy(x=50, y=50, width=100, height=100)
    manager.add(widget1, layer=0)
    manager.add(widget2, layer=1)

    children = list(manager.get_widgets_at(pos=(100, 100)))
    assert children == [widget1]


def test_get_widgets_at_from_specific_layer(window):
    manager = UIManager()
    widget1 = UIDummy(x=50, y=50, width=100, height=100)
    widget2 = UIDummy(x=50, y=50, width=100, height=100)
    manager.add(widget1, layer=0)
    manager.add(widget2, layer=1)

    children = list(manager.get_widgets_at(pos=(60, 60), layer=1))
    assert children == [widget2]


def test_get_widgets_at_from_all_layers(window):
    manager = UIManager()
    widget1 = UIDummy(x=50, y=50, width=100, height=100)
    widget2 = UIDummy(x=50, y=50, width=100, height=100)
    manager.add(widget1, layer=0)
    manager.add(widget2, layer=1)

    children = list(manager.get_widgets_at(pos=(60, 60), layer=None))
    assert children == [widget2, widget1]


def test_get_top_widget_by_cls(window):
    class MyUIDummy(UIDummy):
        pass

    manager = UIManager()
    widget1 = UIDummy(x=50, y=50, width=100, height=100)
    widget2 = MyUIDummy(x=75, y=75, width=50, height=50)
    widget1.add(widget2)
    manager.add(widget1)

    children = list(manager.get_widgets_at(pos=(100, 100)))
    assert children == [widget2, widget1]

    children = list(manager.get_widgets_at(pos=(100, 100), cls=MyUIDummy))
    assert children == [widget2]


def test_remove_child_and_clear_parent_property(window):
    manager = UIManager()
    widget1 = UIDummy()
    manager.add(widget1)

    manager.remove(widget1)

    assert widget1.parent is None
    assert list(manager.walk_widgets()) == []


def test_clear_removes_all_children(window):
    manager = UIManager()
    widget1 = UIDummy(x=50, y=50, width=100, height=100)
    manager.add(widget1)

    widget2 = UIDummy(x=50, y=50, width=100, height=100)
    manager.add(widget2)

    manager.clear()

    assert widget1.parent is None
    assert widget2.parent is None
    assert list(manager.walk_widgets()) == []
