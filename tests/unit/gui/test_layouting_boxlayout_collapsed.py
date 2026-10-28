import pytest

from arcade.gui import UIBoxLayout, UIWidget
from arcade.types import LBWH


@pytest.mark.parametrize("vertical", [False, True])
@pytest.mark.parametrize("count", [0, 1, 3])
def test_all_collapsed_children_preserve_only_padding_and_border(vertical, count):
    children = [UIWidget(width=100, height=50) for _ in range(count)]
    for child in children:
        child.visible = None
    original_rects = [child.rect for child in children]
    box = UIBoxLayout(vertical=vertical, children=children, space_between=10)
    box.with_padding(left=2, right=3, top=5, bottom=7).with_border(width=4)

    box.fit_content()
    box.do_layout()

    assert box.size_hint_min == (13, 20)
    assert box.size == (13, 20)
    assert [child.rect for child in children] == original_rects


@pytest.mark.parametrize("vertical", [False, True])
@pytest.mark.parametrize("collapsed_index", [0, 1, 2])
def test_collapsed_children_do_not_reserve_gaps(vertical, collapsed_index):
    first = UIWidget(size_hint=(1, 1), size_hint_min=(20, 30))
    second = UIWidget(size_hint=(1, 1), size_hint_min=(20, 30))
    collapsed = UIWidget(width=100, height=100)
    collapsed.visible = None
    original_rect = collapsed.rect
    children = [first, second]
    children.insert(collapsed_index, collapsed)
    box = UIBoxLayout(vertical=vertical, children=children, space_between=10)

    assert box.size_hint_min == ((20, 70) if vertical else (50, 30))
    box.rect = LBWH(0, 0, 120, 120)
    box.do_layout()

    if vertical:
        assert first.rect == LBWH(0, 65, 120, 55)
        assert second.rect == LBWH(0, 0, 120, 55)
    else:
        assert first.rect == LBWH(0, 0, 55, 120)
        assert second.rect == LBWH(65, 0, 55, 120)
    assert collapsed.rect == original_rect


@pytest.mark.parametrize("vertical", [False, True])
@pytest.mark.parametrize("visible", [False, True])
def test_hidden_children_still_participate_in_layout(vertical, visible):
    first = UIWidget(width=20, height=30)
    first.visible = visible
    second = UIWidget(width=40, height=50)
    box = UIBoxLayout(vertical=vertical, children=[first, second], space_between=10)

    box.fit_content()
    box.do_layout()

    assert box.size_hint_min == ((40, 90) if vertical else (70, 50))
    if vertical:
        assert first.top == box.top
        assert first.bottom - second.top == 10
        assert second.bottom == box.bottom
    else:
        assert first.left == box.left
        assert second.left - first.right == 10
        assert second.right == box.right


@pytest.mark.parametrize("vertical", [False, True])
def test_visibility_changes_update_the_minimum_size(vertical):
    first = UIWidget(width=20, height=30)
    second = UIWidget(width=40, height=50)
    box = UIBoxLayout(vertical=vertical, children=[first, second], space_between=10)

    first.visible = None
    box._prepare_layout()
    assert box.size_hint_min == (40, 50)

    second.visible = None
    box._prepare_layout()
    assert box.size_hint_min == (0, 0)

    first.visible = False
    box._prepare_layout()
    assert box.size_hint_min == (20, 30)

    second.visible = True
    box._prepare_layout()
    assert box.size_hint_min == ((40, 90) if vertical else (70, 50))


def test_collapse_and_restore_through_ui_manager(window, ui):
    first = UIWidget(width=20, height=30)
    second = UIWidget(width=40, height=50)
    box = UIBoxLayout(children=[first, second], space_between=10)
    ui.add(box)
    ui.execute_layout()
    assert box.size == (40, 90)

    first.visible = None
    ui.execute_layout()
    assert box.size == (40, 50)

    second.visible = None
    ui.execute_layout()
    assert box.size == (0, 0)

    first.visible = False
    ui.execute_layout()
    assert box.size == (20, 30)
