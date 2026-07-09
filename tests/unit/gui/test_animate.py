import pytest

from arcade.anim import Easing
from arcade.gui import UIDummy, UIWidget
from arcade.gui.experimental import Animation, TransitionAttr, UIAnimatedGroup, rel
from arcade.gui.events import UIOnUpdateEvent
from arcade.types import Color


@pytest.fixture(autouse=True)
def _ensure_window(window):
    """UIAnimatedGroup allocates a Surface, which needs the shared window."""


def update(widget: UIWidget, dt: float):
    """Dispatch an update event like the UIManager does."""
    widget.dispatch_ui_event(UIOnUpdateEvent(None, dt))


def make_group() -> UIAnimatedGroup:
    """Create a UIAnimatedGroup to tick animations against."""
    return UIAnimatedGroup(child=UIDummy())


class Subject:
    """Plain object to tick animations against directly."""

    def __init__(self, **values):
        for key, value in values.items():
            setattr(self, key, value)


def test_animate_single_property():
    widget = make_group()
    widget.center = (0, 0)

    widget.animate(center_x=100, duration=1)

    update(widget, 0.5)
    assert widget.center_x == 50

    update(widget, 0.5)
    assert widget.center_x == 100

    # value stays after finishing
    update(widget, 1)
    assert widget.center_x == 100


def test_animate_multiple_properties_in_parallel():
    widget = make_group()
    widget.center = (0, 0)

    widget.animate(center_x=100, center_y=50, duration=1)

    update(widget, 0.5)
    assert widget.center == (50, 25)

    update(widget, 0.5)
    assert widget.center == (100, 50)


def test_animate_captures_current_value_as_start():
    widget = make_group()
    widget.center = (0, 0)

    anim = widget.animate(center_x=100, duration=1, delay=1)

    # start value is read when the animation actually starts, not when created
    update(widget, 0.5)
    widget.center_x = 50
    update(widget, 0.5)
    assert widget.center_x == 50

    update(widget, 0.5)
    assert widget.center_x == 75

    update(widget, 0.5)
    assert widget.center_x == 100
    assert anim.finished


def test_animate_relative_target():
    widget = make_group()
    widget.center = (50, 0)

    widget.animate(center_x=rel(100), duration=1)

    update(widget, 0.5)
    assert widget.center_x == 100

    update(widget, 0.5)
    assert widget.center_x == 150


def test_then_chains_segments():
    widget = make_group()
    widget.center = (0, 0)

    widget.animate(center_x=100, duration=1).then(center_y=50, duration=1)

    update(widget, 1)
    assert widget.center == (100, 0)

    update(widget, 1)
    assert widget.center == (100, 50)


def test_then_consumes_remaining_dt_within_one_update():
    widget = make_group()
    widget.center = (0, 0)

    widget.animate(center_x=100, duration=1).then(center_x=50, duration=1)

    # one big update crosses both segments frame-accurately
    update(widget, 1.5)
    assert widget.center_x == 75

    update(widget, 0.5)
    assert widget.center_x == 50


def test_then_without_properties_acts_as_pause():
    widget = make_group()
    widget.center = (0, 0)

    finished = []
    widget.animate(center_x=100, duration=1).then(duration=1).on_finish(
        lambda: finished.append(True)
    )

    update(widget, 1)
    assert widget.center_x == 100
    assert not finished

    update(widget, 1)
    assert finished == [True]


def test_repeat_re_captures_start_values():
    widget = make_group()
    widget.center = (0, 0)

    # relative targets accumulate over iterations
    widget.animate(center_x=rel(100), duration=1, repeat=1)

    update(widget, 1)
    assert widget.center_x == 100

    update(widget, 1)
    assert widget.center_x == 200

    update(widget, 1)
    assert widget.center_x == 200


def test_infinite_repeat_never_finishes():
    widget = make_group()
    widget.center = (0, 0)

    anim = widget.animate(center_x=rel(100), duration=1, repeat=True)

    for expected in (100, 200, 300):
        update(widget, 1)
        assert widget.center_x == expected

    assert not anim.finished


def test_yoyo_returns_to_start():
    widget = make_group()
    widget.center = (0, 0)

    anim = widget.animate(center_x=100, duration=1, yoyo=True)

    update(widget, 1)
    assert widget.center_x == 100

    update(widget, 0.5)
    assert widget.center_x == 50

    update(widget, 0.5)
    assert widget.center_x == 0
    assert anim.finished


def test_new_animation_takes_over_property():
    widget = make_group()
    widget.center = (0, 0)

    first = widget.animate(center_x=100, center_y=100, duration=1)
    update(widget, 0.5)
    assert widget.center == (50, 50)

    # second animation takes over center_x, first keeps animating center_y
    second = widget.animate(center_x=0, duration=0.5)
    update(widget, 0)  # activate the takeover at the current value
    assert widget.center == (50, 50)

    update(widget, 0.25)
    assert widget.center == (25, 75)

    update(widget, 0.25)
    assert widget.center == (0, 100)
    assert first.finished
    assert second.finished


def test_takeover_stops_endless_animation_without_properties():
    widget = make_group()
    widget.center = (0, 0)

    idle = widget.animate(center_x=rel(100), duration=1, repeat=True)
    update(widget, 0.5)

    # taking over its only property would leave it looping without effect
    widget.animate(center_x=0, duration=0.5)
    update(widget, 0.1)
    assert idle.finished


def test_pending_animation_is_not_overwritten():
    widget = make_group()
    widget.center = (0, 0)

    # delayed animation is not yet active, it claims the property when it starts
    delayed = widget.animate(center_x=100, duration=1, delay=1)
    immediate = widget.animate(center_x=50, duration=0.5)

    update(widget, 0.5)
    assert widget.center_x == 50
    assert immediate.finished

    update(widget, 0.5)  # delay over, delayed animation activates
    update(widget, 1)
    assert widget.center_x == 100
    assert delayed.finished


def test_on_finish_called_once():
    widget = make_group()
    widget.center = (0, 0)

    finished = []
    widget.animate(center_x=100, duration=1).on_finish(lambda: finished.append(True))

    update(widget, 0.5)
    assert finished == []

    update(widget, 0.5)
    assert finished == [True]

    update(widget, 1)
    assert finished == [True]


def test_stop_halts_and_suppresses_on_finish():
    widget = make_group()
    widget.center = (0, 0)

    finished = []
    anim = widget.animate(center_x=100, duration=1).on_finish(lambda: finished.append(True))

    update(widget, 0.5)
    anim.stop()
    update(widget, 1)

    assert widget.center_x == 50
    assert anim.finished
    assert finished == []


def test_zero_duration_applies_immediately():
    widget = make_group()
    widget.center = (0, 0)

    widget.animate(center_x=100, duration=0)
    update(widget, 0)
    assert widget.center_x == 100


def test_color_values_are_interpolated():
    subject = Subject(tint=Color(255, 0, 0, 255))
    anim = Animation(tint=Color(0, 0, 255, 255), duration=1)

    anim.tick(subject, 0.5)
    assert subject.tint == Color(128, 0, 128, 255)
    assert isinstance(subject.tint, Color)

    anim.tick(subject, 0.5)
    assert subject.tint == Color(0, 0, 255, 255)


def test_tuple_values_are_interpolated():
    subject = Subject(anchor=(0.0, 100.0))
    anim = Animation(anchor=(100.0, 0.0), duration=1)

    anim.tick(subject, 0.5)
    assert subject.anchor == (50.0, 50.0)


def test_non_interpolatable_values_snap_at_the_end():
    subject = Subject(disabled=False)
    anim = Animation(disabled=True, duration=1)

    anim.tick(subject, 0.5)
    assert subject.disabled is False

    anim.tick(subject, 0.5)
    assert subject.disabled is True


def test_easing_is_applied():
    subject = Subject(x=0.0)
    anim = Animation(x=100.0, duration=1, ease=Easing.SINE)

    anim.tick(subject, 0.5)
    assert subject.x != 50.0  # non-linear
    assert 0 < subject.x < 100

    anim.tick(subject, 0.5)
    assert subject.x == 100.0


def test_animation_composes_with_low_level_transitions():
    widget = make_group()
    widget.center = (0, 0)

    # Animation implements the TransitionBase protocol
    widget.add_transition(
        Animation(center_x=100, duration=1)
        + TransitionAttr(attribute="center_y", end=50, duration=1)
    )

    update(widget, 1)
    assert widget.center == (100, 0)

    update(widget, 1)
    assert widget.center == (100, 50)
