from unittest.mock import Mock

from arcade.gui import (
    UIWidget, TransitionAttr, TransitionChain, EventTransitionBase,
    TransitionParallel, TransitionDelay, TransitionAttrIncr, TransitionAttrSet
)


def test_move_widget():
    widget = UIWidget()
    assert widget.center_x == 50

    widget.add_transition(TransitionAttr(attribute="center_x", start=0, end=100, duration=2))

    # set start value
    widget.dispatch_event("on_update", 0.0)
    assert widget.center_x == 0

    # update value
    widget.dispatch_event("on_update", 0.1)
    assert widget.center_x == 5

    # reach 50%
    widget.dispatch_event("on_update", 0.9)
    assert widget.center_x == 50

    # do not overshoot
    widget.dispatch_event("on_update", 1.1)
    assert widget.center_x == 100

    # do not change value
    widget.dispatch_event("on_update", 1)
    assert widget.center_x == 100


def test_transition_chain_perfect_update_interval():
    widget = UIWidget()
    assert widget.center_x == 50

    chain = widget.add_transition(TransitionChain())
    chain.add(TransitionAttr(attribute="center_x", end=100, duration=1))
    chain.add(TransitionAttr(attribute="center_x", end=50, duration=1))
    chain.add(TransitionAttr(attribute="center_x", end=150, duration=1))
    chain.add(TransitionAttr(attribute="center_x", end=200, duration=1))

    widget.dispatch_event("on_update", 1)
    assert widget.center_x == 100

    widget.dispatch_event("on_update", 1)
    assert widget.center_x == 50

    widget.dispatch_event("on_update", 1)
    assert widget.center_x == 150

    widget.dispatch_event("on_update", 1)
    assert widget.center_x == 200


def test_transition_chain_split_update_interval():
    widget = UIWidget()
    assert widget.center_x == 50

    chain = widget.add_transition(TransitionChain())
    chain.add(TransitionAttr(attribute="center_x", end=100, duration=1))
    chain.add(TransitionAttr(attribute="center_x", end=50, duration=1))

    widget.dispatch_event("on_update", 2)
    assert widget.center_x == 50


def test_parallel_transition():
    widget = UIWidget()
    widget.center = (0, 0)

    parallel = widget.add_transition(TransitionParallel())
    parallel.add(TransitionAttr(attribute="center_x", end=100, duration=1))
    parallel.add(TransitionAttr(attribute="center_y", end=50, duration=1))

    widget.dispatch_event("on_update", 0.5)
    assert widget.center == (50, 25)

    widget.dispatch_event("on_update", 0.5)
    assert widget.center == (100, 50)


def test_parallel_returns_remaining_dt():
    widget = UIWidget()
    widget.center = (0, 0)

    parallel = widget.add_transition(TransitionParallel())
    parallel.add(TransitionAttr(attribute="center_x", end=100, duration=1.5))
    parallel.add(TransitionAttr(attribute="center_y", end=50, duration=1))

    remaining_dt = parallel.tick(widget, 1)
    assert remaining_dt == 0

    remaining_dt = parallel.tick(widget, 1)
    assert remaining_dt == 0.5


def test_transition_chain_with_delay():
    widget = UIWidget()
    widget.center = (0, 0)

    chain = widget.add_transition(TransitionChain())
    chain.add(TransitionDelay(duration=1.5))
    chain.add(TransitionAttr(attribute="center_y", end=50, duration=1))

    widget.dispatch_event("on_update", 1)
    assert widget.center_y == 0

    widget.dispatch_event("on_update", 0.5)
    assert widget.center_y == 0

    widget.dispatch_event("on_update", 1)
    assert widget.center_y == 50


def test_event_transaction_base_dispatching():
    widget = UIWidget()
    widget.center = (0, 0)

    et = widget.add_transition(EventTransitionBase(duration=1))

    et.on_tick = Mock()
    et.on_finish = Mock()

    widget.dispatch_event("on_update", 0.5)

    assert et.on_tick.called
    assert not et.on_finish.called

    widget.dispatch_event("on_update", 0.5)
    assert et.on_tick.called
    assert et.on_finish.called


def test_transition_attr_increment():
    widget = UIWidget()
    widget.center = (50, 0)

    widget.add_transition(TransitionAttrIncr(attribute="center_x", increment=100, duration=1))

    widget.dispatch_event("on_update", 0.5)
    assert widget.center_x == 100

    widget.dispatch_event("on_update", 0.5)
    assert widget.center_x == 150


def test_transition_attr_setter():
    widget = UIWidget()
    widget.center = (50, 0)

    widget.add_transition(TransitionAttrSet(attribute="visible", value=False, duration=1))

    widget.dispatch_event("on_update", 0.5)
    assert widget.visible is True

    widget.dispatch_event("on_update", 0.5)
    assert widget.visible is False


def test_operation_syntax_parallel():
    widget = UIWidget()
    widget.center = (0, 0)

    widget.add_transition(
        TransitionAttrIncr(attribute="center_x", increment=100, duration=1)
        + TransitionAttrIncr(attribute="center_x", increment=100, duration=1)
    )

    widget.dispatch_event("on_update", 1)
    assert widget.center_x == 100

    widget.dispatch_event("on_update", 1)
    assert widget.center_x == 200


def test_operation_syntax_chain():
    widget = UIWidget()
    widget.center = (0, 0)

    widget.add_transition(
        TransitionAttrIncr(attribute="center_x", increment=100, duration=1)
        | TransitionAttrIncr(attribute="center_x", increment=100, duration=1)
    )

    widget.dispatch_event("on_update", 1)
    assert widget.center_x == 200
