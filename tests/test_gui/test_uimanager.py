from arcade.gui import UIManager, UIDummy


def test_iterate_children_flat(window):
    manager = UIManager()
    widget1 = UIDummy()
    manager.add(widget1)

    children = list(child for child in manager.walk_widgets())

    assert children == [widget1]


def test_iterate_children_tree(window):
    manager = UIManager()
    widget1 = UIDummy()
    widget2 = UIDummy()
    widget1.add(widget2)
    manager.add(widget1)

    children = list(manager.walk_widgets())

    assert children == [widget2, widget1]


def test_get_top_widget(window):
    manager = UIManager()
    widget1 = UIDummy(x=50, y=50, width=100, height=100)
    widget2 = UIDummy(x=75, y=75, width=50, height=50)
    widget1.add(widget2)
    manager.add(widget1)

    children = list(manager.get_widgets_at(pos=(100, 100)))
    assert children == [widget2, widget1]

    children = list(manager.get_widgets_at(pos=(60, 60)))
    assert children == [widget1]


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
