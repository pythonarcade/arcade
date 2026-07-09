from unittest.mock import Mock

import pytest

from arcade.gui import UIDummy, UIWidget
from arcade.gui.experimental import (
    TransitionAttr,
    TransitionChain,
    EventTransitionBase,
    TransitionParallel,
    TransitionDelay,
    TransitionAttrIncr,
    TransitionAttrSet,
    UIAnimatedGroup,
)
from arcade.gui.events import UIOnUpdateEvent


def update(widget: UIWidget, dt: float):
    """Dispatch an update event like the UIManager does."""
    widget.dispatch_ui_event(UIOnUpdateEvent(None, dt))


@pytest.fixture(autouse=True)
def _ensure_window(window):
    """UIAnimatedGroup allocates a Surface, which needs the shared window."""


def make_group() -> UIAnimatedGroup:
    """Create a UIAnimatedGroup to tick transitions against."""
    return UIAnimatedGroup(child=UIDummy())


def test_move_widget():
    widget = make_group()
    assert widget.center_x == 50

    widget.add_transition(TransitionAttr(attribute="center_x", start=0, end=100, duration=2))

    # set start value
    update(widget, 0.0)
    assert widget.center_x == 0

    # update value
    update(widget, 0.1)
    assert widget.center_x == 5

    # reach 50%
    update(widget, 0.9)
    assert widget.center_x == 50

    # do not overshoot
    update(widget, 1.1)
    assert widget.center_x == 100

    # do not change value
    update(widget, 1)
    assert widget.center_x == 100


def test_transition_chain_perfect_update_interval():
    widget = make_group()
    assert widget.center_x == 50

    chain = widget.add_transition(TransitionChain())
    chain.add(TransitionAttr(attribute="center_x", end=100, duration=1))
    chain.add(TransitionAttr(attribute="center_x", end=50, duration=1))
    chain.add(TransitionAttr(attribute="center_x", end=150, duration=1))
    chain.add(TransitionAttr(attribute="center_x", end=200, duration=1))

    update(widget, 1)
    assert widget.center_x == 100

    update(widget, 1)
    assert widget.center_x == 50

    update(widget, 1)
    assert widget.center_x == 150

    update(widget, 1)
    assert widget.center_x == 200


def test_transition_chain_split_update_interval():
    widget = make_group()
    assert widget.center_x == 50

    chain = widget.add_transition(TransitionChain())
    chain.add(TransitionAttr(attribute="center_x", end=100, duration=1))
    chain.add(TransitionAttr(attribute="center_x", end=50, duration=1))

    update(widget, 2)
    assert widget.center_x == 50


def test_parallel_transition():
    widget = make_group()
    widget.center = (0, 0)

    parallel = widget.add_transition(TransitionParallel())
    parallel.add(TransitionAttr(attribute="center_x", end=100, duration=1))
    parallel.add(TransitionAttr(attribute="center_y", end=50, duration=1))

    update(widget, 0.5)
    assert widget.center == (50, 25)

    update(widget, 0.5)
    assert widget.center == (100, 50)


def test_parallel_returns_remaining_dt():
    widget = make_group()
    widget.center = (0, 0)

    parallel = widget.add_transition(TransitionParallel())
    parallel.add(TransitionAttr(attribute="center_x", end=100, duration=1.5))
    parallel.add(TransitionAttr(attribute="center_y", end=50, duration=1))

    remaining_dt = parallel.tick(widget, 1)
    assert remaining_dt == 0

    remaining_dt = parallel.tick(widget, 1)
    assert remaining_dt == 0.5


def test_transition_chain_with_delay():
    widget = make_group()
    widget.center = (0, 0)

    chain = widget.add_transition(TransitionChain())
    chain.add(TransitionDelay(duration=1.5))
    chain.add(TransitionAttr(attribute="center_y", end=50, duration=1))

    update(widget, 1)
    assert widget.center_y == 0

    update(widget, 0.5)
    assert widget.center_y == 0

    update(widget, 1)
    assert widget.center_y == 50


def test_event_transaction_base_dispatching():
    widget = make_group()
    widget.center = (0, 0)

    et = widget.add_transition(EventTransitionBase(duration=1))

    et.on_tick = Mock()
    et.on_finish = Mock()

    update(widget, 0.5)

    assert et.on_tick.called
    assert not et.on_finish.called

    update(widget, 0.5)
    assert et.on_tick.called
    assert et.on_finish.called


def test_transition_attr_increment():
    widget = make_group()
    widget.center = (50, 0)

    widget.add_transition(TransitionAttrIncr(attribute="center_x", increment=100, duration=1))

    update(widget, 0.5)
    assert widget.center_x == 100

    update(widget, 0.5)
    assert widget.center_x == 150


def test_transition_attr_setter():
    widget = make_group()
    widget.center = (50, 0)

    widget.add_transition(TransitionAttrSet(attribute="visible", value=False, duration=1))

    update(widget, 0.5)
    assert widget.visible is True

    update(widget, 0.5)
    assert widget.visible is False


def test_operation_syntax_parallel():
    widget = make_group()
    widget.center = (0, 0)

    widget.add_transition(
        TransitionAttrIncr(attribute="center_x", increment=100, duration=1)
        + TransitionAttrIncr(attribute="center_x", increment=100, duration=1)
    )

    update(widget, 1)
    assert widget.center_x == 100

    update(widget, 1)
    assert widget.center_x == 200


def test_operation_syntax_chain():
    widget = make_group()
    widget.center = (0, 0)

    widget.add_transition(
        TransitionAttrIncr(attribute="center_x", increment=100, duration=1)
        | TransitionAttrIncr(attribute="center_x", increment=100, duration=1)
    )

    update(widget, 1)
    assert widget.center_x == 200
