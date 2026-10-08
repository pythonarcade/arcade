"""High level animation API for GUI widgets.

:class:`Animation` tweens widget properties over time. Animations are usually
created via :meth:`~arcade.gui.experimental.UIAnimatedGroup.animate` and are
ticked by the group itself, no manual update calls are required.

.. code-block:: python

    # scale and fade in, then wiggle once
    group.animate(scale=1.0, alpha=255, duration=0.5, ease=Easing.BACK_OUT)
    group.animate(angle=3, duration=0.1).then(angle=-3, duration=0.2).then(angle=0, duration=0.1)

The lower level building blocks live in :mod:`arcade.gui.experimental.transition`.
"""

from __future__ import annotations

from typing import Any, Callable

from arcade.anim import Easing
from arcade.anim.easing import EasingFunction
from arcade.gui.experimental.transition import TransitionBase
from arcade.types import Color

__all__ = ["Animation", "rel"]


class _Relative:
    """Marks an animation target value as relative to the current value."""

    __slots__ = ("value",)

    def __init__(self, value: float):
        self.value = value

    def __repr__(self) -> str:
        return f"rel({self.value!r})"


def rel(value: float) -> _Relative:
    """Mark an animation target as relative to the property's current value.

    .. code-block:: python

        # rotate 360 degrees counterclockwise from wherever the widget is now,
        # forever (each iteration adds another turn)
        widget.animate(angle=rel(-360), duration=8, repeat=True)

    Only numeric values (and types supporting ``current + value``) can be
    relative.

    Args:
        value: Offset added to the current value when the animation starts.
    """
    return _Relative(value)


def _lerp_value(start: Any, end: Any, factor: float) -> Any:
    """Interpolate between two values, dispatching on their type.

    Supports numbers, :class:`~arcade.types.Color` (channel-wise, clamped),
    plain tuples/lists (element-wise) and any type implementing ``+``, ``-``
    and scalar ``*`` (e.g. ``pyglet.math.Vec2``). Values which cannot be
    interpolated (e.g. ``bool`` or ``str``) snap to ``end`` when the
    animation reaches its target.
    """
    # bool is an int subclass, treat it as a step value instead
    if isinstance(start, bool) or isinstance(end, bool):
        return end if factor >= 1.0 else start

    # Color is a tuple subclass, check before the generic sequence case
    if isinstance(start, Color) or isinstance(end, Color):
        a = Color.from_iterable(start)
        b = Color.from_iterable(end)
        return Color(*(min(255, max(0, round(ca + (cb - ca) * factor))) for ca, cb in zip(a, b)))

    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
        return start + (end - start) * factor

    if isinstance(start, (tuple, list)) and isinstance(end, (tuple, list)):
        return tuple(_lerp_value(s, e, factor) for s, e in zip(start, end))

    try:
        return start + (end - start) * factor
    except TypeError:
        return end if factor >= 1.0 else start


class _Segment:
    """One step of an :class:`Animation`: a set of property targets plus timing."""

    __slots__ = ("targets", "duration", "delay", "ease", "elapsed", "captured", "tweens")

    def __init__(
        self,
        targets: dict[str, Any],
        duration: float,
        delay: float,
        ease: EasingFunction,
    ):
        self.targets = targets
        self.duration = duration
        self.delay = delay
        self.ease = ease

        self.elapsed: float | None = None
        self.captured: bool = False
        self.tweens: dict[str, tuple[Any, Any]] = {}
        self.reset()

    def reset(self):
        """Reset runtime state, start values are re-captured on next activation."""
        self.elapsed = None
        self.captured = False
        self.tweens = {}


class Animation(TransitionBase):
    """Tweens one or more properties of a widget over time.

    Use :meth:`arcade.gui.experimental.UIAnimatedGroup.animate` to create and
    start an animation:

    .. code-block:: python

        anim = widget.animate(scale=1.08, angle=2.5, duration=0.15, ease=Easing.BACK_OUT)
        anim.then(scale=1.0, angle=0.0, duration=0.15)   # runs afterwards
        anim.on_finish(lambda: print("done"))
        anim.stop()                                       # cancel this animation only

    Start values are read from the widget when a segment starts, so animations
    always continue smoothly from the current state. To animate from a fixed
    value, set the property before animating
    (``widget.alpha = 0; widget.animate(alpha=255)``).

    **Conflicts are resolved per property**: when a segment starts, it takes
    ownership of its properties and other running animations stop touching
    them - the rest of their properties keep animating. This means starting a
    new animation "wins" without cancelling unrelated animations.

    An :class:`Animation` implements the
    :class:`~arcade.gui.experimental.TransitionBase` protocol and can be
    combined with the low level transition classes via ``+`` (sequential)
    and ``|`` (parallel).

    Args:
        duration: Duration of the first segment in seconds.
        ease: Easing function for the first segment, see :class:`arcade.anim.Easing`.
        delay: Seconds to wait before the first segment starts.
        repeat: How often to repeat the whole animation after its first run.
            ``True`` or a negative value repeats forever. Each iteration
            re-reads the start values, so relative targets (:func:`rel`)
            accumulate.
        yoyo: If True, the animation plays backwards to its start values
            before it finishes (or repeats).
        **properties: Attribute names mapped to target values, e.g.
            ``scale=1.0, alpha=255``. Values wrapped in :func:`rel` are
            relative to the current value. A segment without properties acts
            as a pause.
    """

    def __init__(
        self,
        *,
        duration: float = 0.3,
        ease: EasingFunction = Easing.LINEAR,
        delay: float = 0.0,
        repeat: int | bool = 0,
        yoyo: bool = False,
        **properties: Any,
    ):
        self._segments: list[_Segment] = []
        self._index = 0
        self._backward = False
        self._yoyo = yoyo
        self._repeat = -1 if repeat is True else int(repeat)
        self._finished = False
        self._callbacks: list[Callable[[], Any]] = []
        self._callbacks_fired = False

        self.then(duration=duration, ease=ease, delay=delay, **properties)

    def then(
        self,
        *,
        duration: float = 0.3,
        ease: EasingFunction = Easing.LINEAR,
        delay: float = 0.0,
        **properties: Any,
    ) -> "Animation":
        """Append a segment which runs after the previous one finished.

        Accepts the same arguments as the constructor (except ``repeat`` and
        ``yoyo``, which apply to the whole animation). A ``then()`` without
        properties acts as a pause:

        .. code-block:: python

            widget.animate(alpha=0, duration=0.5).then(duration=0.1).on_finish(arcade.exit)

        Returns:
            The animation itself, for method chaining.
        """
        self._segments.append(_Segment(dict(properties), float(duration), float(delay), ease))
        return self

    def on_finish(self, callback: Callable[[], Any]) -> "Animation":
        """Register a callback invoked once when the animation completes.

        Not invoked when the animation is stopped via :meth:`stop` or
        overwritten by other animations. Endlessly repeating animations
        never finish.

        Args:
            callback: Callable without arguments.

        Returns:
            The animation itself, for method chaining.
        """
        self._callbacks.append(callback)
        return self

    def stop(self) -> None:
        """Stop the animation, leaving the properties at their current values.

        The widget removes stopped animations automatically.
        ``on_finish`` callbacks are not invoked.
        """
        self._finished = True
        self._callbacks_fired = True

    @property
    def finished(self) -> bool:
        """True if the animation completed or was stopped."""
        return self._finished

    def tick(self, subject: Any, dt: float) -> float:
        """Advance the animation, called by the owning widget.

        Returns:
            dt, which was not consumed
        """
        if self._finished:
            return dt

        remaining = float(dt)
        last_wrap_budget: float | None = None

        while not self._finished:
            segment = self._segments[self._index]
            leftover = self._tick_segment(subject, segment, remaining)
            if leftover is None:
                # segment consumed all time and is still running
                return 0.0

            remaining = leftover
            if self._advance():
                # a full iteration completed; if it consumed no time
                # (all segments have zero duration), stop looping this frame
                if not self._finished:
                    if last_wrap_budget is not None and remaining >= last_wrap_budget:
                        return 0.0
                    last_wrap_budget = remaining

            if remaining <= 0.0 and not self._finished:
                return 0.0

        self._fire_finished()
        return remaining

    def _tick_segment(self, subject: Any, segment: _Segment, dt: float) -> float | None:
        """Advance a single segment.

        Returns:
            Leftover dt if the segment finished, otherwise None.
        """
        if segment.elapsed is None:
            # delays are only honored when playing forward
            segment.elapsed = 0.0 if self._backward else -segment.delay
        segment.elapsed += dt

        if segment.elapsed < 0:
            return None

        if not segment.captured:
            self._capture(subject, segment)

        if segment.duration > 0:
            progress = min(segment.elapsed / segment.duration, 1.0)
        else:
            progress = 1.0
        # playing backward mirrors the value trajectory in time
        t = 1.0 - progress if self._backward else progress
        factor = segment.ease(t)

        for name, (start, end) in segment.tweens.items():
            setattr(subject, name, _lerp_value(start, end, factor))

        if segment.elapsed >= segment.duration:
            return segment.elapsed - segment.duration
        return None

    def _capture(self, subject: Any, segment: _Segment) -> None:
        """Read start values and take ownership of the segment's properties.

        Other running animations on the subject stop touching these
        properties ("whoever starts last wins the property").
        """
        segment.captured = True
        segment.tweens = {}
        for name, target in segment.targets.items():
            start = getattr(subject, name)
            end = start + target.value if isinstance(target, _Relative) else target
            segment.tweens[name] = (start, end)

        if segment.targets:
            for other in getattr(subject, "_transitions", None) or []:
                if other is not self and isinstance(other, Animation):
                    other._remove_properties(segment.targets.keys())

    def _remove_properties(self, names) -> None:
        """Stop animating the given properties in the currently active segment.

        Pending segments keep their targets, they re-claim the properties
        when they activate. An endlessly repeating animation which lost all
        of its properties is stopped, otherwise it would loop forever
        without effect.
        """
        if self._finished or not self._segments:
            return
        segment = self._segments[self._index]
        if not segment.captured:
            return
        for name in names:
            segment.targets.pop(name, None)
            segment.tweens.pop(name, None)

        if self._repeat < 0 and not any(s.targets for s in self._segments):
            self.stop()

    def _advance(self) -> bool:
        """Move to the next segment.

        Returns:
            True when a full iteration (including the yoyo pass) completed.
        """
        if self._backward:
            if self._index > 0:
                self._index -= 1
                self._segments[self._index].elapsed = None
                return False
            return self._complete_iteration()

        if self._index + 1 < len(self._segments):
            self._index += 1
            return False

        if self._yoyo:
            self._backward = True
            self._segments[self._index].elapsed = None
            return False

        return self._complete_iteration()

    def _complete_iteration(self) -> bool:
        if self._repeat != 0:
            if self._repeat > 0:
                self._repeat -= 1
            self._backward = False
            self._index = 0
            for segment in self._segments:
                segment.reset()
            return True

        self._finished = True
        return True

    def _fire_finished(self) -> None:
        if self._callbacks_fired:
            return
        self._callbacks_fired = True
        for callback in self._callbacks:
            callback()
