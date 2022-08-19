from arcade.gui import UIDummy, UIBoxLayout
from arcade.gui.widgets.layout import UIAnchorLayout


def test_place_widget(window):
    dummy = UIDummy(width=100, height=200)

    subject = UIAnchorLayout(
        x=0,
        y=0,
        width=500,
        height=500
    )

    subject.add(
        dummy,
        align_x=10,
        anchor_x="center_x",
        align_y=-20,
        anchor_y="top",
    )

    subject.do_layout()

    assert subject.rect == (0, 0, 500, 500)

    assert dummy.center_x == 260
    assert dummy.top == 480


def test_place_widget_relative_to_own_content_rect(window):
    dummy = UIDummy(width=100, height=200)

    subject = UIAnchorLayout(
        x=0,
        y=0,
        width=500,
        height=500
    ).with_border(
        width=2
    ).with_padding(left=50, top=100)

    subject.add(
        dummy,
        align_x=10,
        anchor_x="left",
        align_y=-20,
        anchor_y="top",
    )

    subject.do_layout()

    assert subject.rect == (0, 0, 500, 500)

    assert dummy.left == 62
    assert dummy.top == 378


def test_place_box_layout(window):
    subject = UIAnchorLayout(width=500, height=500)

    box = UIBoxLayout()
    box.add(UIDummy(width=100, height=100))
    box.add(UIDummy(width=100, height=100))

    subject.add(child=box, anchor_x="center_x", align_y=-20, anchor_y="top")

    subject._do_layout()

    assert subject.rect == (0, 0, 500, 500)
    assert box.rect == (200, 280, 100, 200)


def test_grow_child_half(window):
    subject = UIAnchorLayout(width=400, height=400)
    dummy = subject.add(UIDummy(width=100, height=100, size_hint=(0.5, 0.5)))

    subject._do_layout()

    assert subject.rect == (0, 0, 400, 400)
    assert dummy.rect == (100, 100, 200, 200)


def test_grow_child_full(window):
    subject = UIAnchorLayout(width=400, height=400)
    dummy = subject.add(UIDummy(width=100, height=100, size_hint=(1, 1)))

    subject._do_layout()

    assert subject.rect == (0, 0, 400, 400)
    assert dummy.rect == (0, 0, 400, 400)


def test_grow_child_to_max_size(window):
    subject = UIAnchorLayout(width=400, height=400)
    dummy = subject.add(UIDummy(width=100, height=100, size_hint=(1, 1), size_hint_max=(200, 150)))

    subject._do_layout()

    assert subject.rect == (0, 0, 400, 400)
    assert dummy.size == (200, 150)


def test_shring_child_to_min_size(window):
    subject = UIAnchorLayout(width=400, height=400)
    dummy = subject.add(UIDummy(width=100, height=100, size_hint=(0.1, 0.1), size_hint_min=(200, 150)))

    subject._do_layout()

    assert subject.rect == (0, 0, 400, 400)
    assert dummy.size == (200, 150)


def test_grow_child_within_bounds(window):
    subject = UIAnchorLayout(width=400, height=400)
    dummy = subject.add(UIDummy(width=100, height=100, size_hint=(2, 2)))

    subject._do_layout()

    assert subject.rect == (0, 0, 400, 400)
    assert dummy.size == (400, 400)


def test_only_adjust_size_if_size_hint_is_given_for_dimension(window):
    subject = UIAnchorLayout(width=400, height=400)
    dummy = subject.add(UIDummy(width=100, height=100, size_hint=(2, None), size_hint_min=(None, 200)))

    subject._do_layout()

    assert subject.rect == (0, 0, 400, 400)
    assert dummy.size == (400, 100)
