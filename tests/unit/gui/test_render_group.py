import pytest

from arcade.gui import (
    Surface,
    UIDummy,
    UIMouseMovementEvent,
    UIMousePressEvent,
)
from arcade.gui.events import UIOnUpdateEvent
from arcade.gui.experimental import Animation, UIAnimatedGroup
from arcade.gui.experimental.group import UIRenderGroup
from arcade.types import LBWH

from . import record_ui_events


class CountingWidget(UIDummy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.render_count = 0

    def do_render(self, surface):
        self.render_count += 1
        super().do_render(surface)


@pytest.fixture
def surface(window):
    return Surface(size=window.get_size())


def test_only_single_child_allowed(window):
    group = UIRenderGroup(child=UIDummy())

    with pytest.raises(ValueError):
        group.add(UIDummy())


def test_delegates_size_hints_to_child(window):
    child = UIDummy(size_hint=(0.5, 1), size_hint_min=(10, 20), size_hint_max=(100, 200))
    group = UIRenderGroup(child=child)

    assert group.size_hint == (0.5, 1)
    assert group.size_hint_min == (10, 20)
    assert group.size_hint_max == (100, 200)


def test_child_is_positioned_in_local_space(window):
    child = UIDummy(width=100, height=50)
    group = UIRenderGroup(child=child)
    group.rect = LBWH(200, 100, 100, 50)

    group._do_layout()

    assert child.rect == LBWH(0, 0, 100, 50)


def test_child_only_rerendered_on_demand(window, surface):
    child = CountingWidget(width=100, height=50)
    group = UIRenderGroup(child=child)
    group.rect = LBWH(0, 0, 100, 50)
    group._do_layout()

    # first render, child is rendered into the internal surface
    with surface.activate():
        rendered = group._do_render(surface, force=True)
    assert rendered is True
    assert child.render_count == 1

    # nothing changed, nothing is rendered
    with surface.activate():
        rendered = group._do_render(surface)
    assert rendered is False
    assert child.render_count == 1

    # forced render from outside only draws the cached surface
    with surface.activate():
        rendered = group._do_render(surface, force=True)
    assert rendered is True
    assert child.render_count == 1

    # transformation change only draws the cached surface
    group.angle = 45
    with surface.activate():
        rendered = group._do_render(surface)
    assert rendered is True
    assert child.render_count == 1

    # child change re-renders the internal surface
    child.trigger_render()
    with surface.activate():
        rendered = group._do_render(surface)
    assert rendered is True
    assert child.render_count == 2


def test_mouse_events_translated_into_local_space(window):
    child = UIDummy(width=100, height=100)
    group = UIRenderGroup(child=child)
    group.rect = LBWH(200, 100, 100, 100)
    group._do_layout()

    with record_ui_events(child, "on_event") as events:
        group.dispatch_ui_event(UIMousePressEvent(None, x=250, y=150, button=1, modifiers=0))

    event = events[-1]
    assert (event.x, event.y) == (50, 50)


def test_mouse_events_adjusted_by_angle(window):
    child = UIDummy(width=100, height=100)
    group = UIRenderGroup(child=child)
    group.rect = LBWH(0, 0, 100, 100)
    group._do_layout()
    group.angle = 90

    # local (100, 50) is rotated 90 degrees ccw around (50, 50) to (50, 100)
    with record_ui_events(child, "on_event") as events:
        group.dispatch_ui_event(UIMouseMovementEvent(None, x=50, y=100, dx=10, dy=0))

    event = events[-1]
    assert (event.x, event.y) == (100, 50)
    assert (event.dx, event.dy) == (0, -10)


def test_mouse_events_adjusted_by_scale(window):
    child = UIDummy(width=100, height=100)
    group = UIRenderGroup(child=child)
    group.rect = LBWH(0, 0, 100, 100)
    group._do_layout()
    group.scale = 0.5

    # local (0, 0) is scaled towards the center (50, 50) to (25, 25)
    with record_ui_events(child, "on_event") as events:
        group.dispatch_ui_event(UIMousePressEvent(None, x=25, y=25, button=1, modifiers=0))

    event = events[-1]
    assert (event.x, event.y) == (0, 0)


def test_mouse_events_not_passed_with_scale_zero(window):
    child = UIDummy(width=100, height=100)
    group = UIRenderGroup(child=child)
    group.rect = LBWH(0, 0, 100, 100)
    group._do_layout()
    group.scale = 0

    with record_ui_events(child, "on_event") as events:
        group.dispatch_ui_event(UIMousePressEvent(None, x=50, y=50, button=1, modifiers=0))

    assert events == []


def test_interactive_group_hover_uses_parent_space(window):
    # The group lives away from the origin; its own hover hit-test must run
    # against ``self.rect`` in parent space, not the child-local space the
    # event is transformed into before being passed to the child subtree.
    child = UIDummy(width=100, height=100)
    group = UIAnimatedGroup(child=child)
    group.rect = LBWH(200, 100, 100, 100)
    group._do_layout()

    group.dispatch_ui_event(UIMouseMovementEvent(None, x=250, y=150, dx=0, dy=0))
    assert group.hovered is True

    group.dispatch_ui_event(UIMouseMovementEvent(None, x=10, y=10, dx=0, dy=0))
    assert group.hovered is False


def test_interactive_group_hover_independent_of_transform(window):
    # Scaling the group must not move its trigger zone: hover is decided by the
    # untransformed event against the base rect, while the child still receives
    # the transformed event.
    child = UIDummy(width=100, height=100)
    group = UIAnimatedGroup(child=child)
    group.rect = LBWH(0, 0, 100, 100)
    group._do_layout()
    group.scale = 1.5

    group.dispatch_ui_event(UIMouseMovementEvent(None, x=50, y=50, dx=0, dy=0))
    assert group.hovered is True


def test_animate_returns_animation(window):
    group = UIAnimatedGroup(child=UIDummy(width=100, height=100))

    animation = group.animate(scale=1.5, duration=1)

    assert isinstance(animation, Animation)


def test_update_event_advances_animation(window):
    # dispatching an update event through the group ticks its animations
    group = UIAnimatedGroup(child=UIDummy(width=100, height=100))
    group.scale = 1.0

    group.animate(scale=2.0, duration=1)

    group.dispatch_ui_event(UIOnUpdateEvent(None, 0.5))
    assert group.scale == 1.5

    group.dispatch_ui_event(UIOnUpdateEvent(None, 0.5))
    assert group.scale == 2.0
