from dataclasses import replace
from math import cos, radians, sin
from typing import Any, TypeVar

from pyglet.event import EVENT_UNHANDLED

from arcade.anim import Easing
from arcade.anim.easing import EasingFunction
from arcade.color import TRANSPARENT_BLACK, WHITE
from arcade.gui.events import (
    UIEvent,
    UIMouseDragEvent,
    UIMouseEvent,
    UIMouseMovementEvent,
    UIOnUpdateEvent,
)
from arcade.gui.experimental.animate import Animation
from arcade.gui.experimental.transition import TransitionBase
from arcade.gui.property import AliasProperty, Property, bind
from arcade.gui.surface import Surface
from arcade.gui.widgets import UIInteractiveWidget, UILayout, UIWidget, W
from arcade.types import LBWH, Point2

__all__ = ["UIRenderGroup", "UIAnimatedGroup"]

T = TypeVar("T", bound=TransitionBase)


class UIRenderGroup(UILayout):
    """A widget that renders its single child onto an internal surface.

    The surface is then drawn into the parent surface at render time
    with applied transformations (rotation, alpha, scale, tint).
    This makes it cheap to animate a whole subtree of widgets:
    as long as the child subtree does not change, only the cached
    surface is drawn again, the child widgets are not re-rendered.

    The child is positioned at the bottom left of the group and resized
    to fill it, so the subtree lives in a local coordinate system
    starting at (0, 0). Mouse events are converted into this local
    coordinate system (including the inverse of rotation and scaling)
    before they are passed to the child.

    Only allows a single child. ``size_hint``, ``size_hint_min`` and
    ``size_hint_max`` are delegated to the child.
    """

    angle = Property(0.0)
    """Rotation in degrees applied around ``anchor``."""
    anchor = Property[Point2 | None](None)
    """Point (in local coordinates) to rotate and scale around.
    Defaults to the center of the group."""
    alpha = Property(255)
    """Alpha value (0-255) applied to the whole subtree."""
    scale = Property(1.0)  # type: ignore  # intentionally shadows UIWidget.scale()
    """Scale factor applied around ``anchor``.
    Shadows :meth:`UIWidget.scale`, which resizes the rect instead."""
    tint = Property(WHITE)
    """Color multiplier applied to the whole subtree."""
    offset_x = Property(0.0)
    """Horizontal translation offset applied when drawing the cached surface.
    Positive values shift the subtree to the right."""
    offset_y = Property(0.0)
    """Vertical translation offset applied when drawing the cached surface.
    Positive values shift the subtree upward."""

    _SizeHint = tuple[float | None, float | None] | None
    size_hint = AliasProperty[_SizeHint]("child", "size_hint")
    size_hint_min = AliasProperty[_SizeHint]("child", "size_hint_min")
    size_hint_max = AliasProperty[_SizeHint]("child", "size_hint_max")
    # rect = AliasProperty[Rect]("child", "rect")

    def __init__(self, *, child: UIWidget, **kwargs):
        # child has to be added before super().__init__,
        # so the size_hint AliasProperties can delegate to it
        self.add(child)

        # UIWidget.__init__ assigns the size_hint arguments unconditionally,
        # which would write through the alias and clobber the child's hints
        hints = (child.size_hint, child.size_hint_min, child.size_hint_max)
        super().__init__(children=tuple(), **kwargs)
        self.size_hint = kwargs.get("size_hint") or hints[0]
        self.size_hint_min = kwargs.get("size_hint_min") or hints[1]
        self.size_hint_max = kwargs.get("size_hint_max") or hints[2]
        # start with a minimal surface, it is resized during rendering
        self._surface = Surface(size=(1, 1))

        # changes of these properties only require to draw the cached surface
        # again, but the area below has to be re-rendered by the parents
        bind(self, "angle", UIRenderGroup.trigger_full_render)
        bind(self, "anchor", UIRenderGroup.trigger_full_render)
        bind(self, "alpha", UIRenderGroup.trigger_full_render)
        bind(self, "scale", UIRenderGroup.trigger_full_render)
        bind(self, "tint", UIRenderGroup.trigger_full_render)
        bind(self, "offset_x", UIRenderGroup.trigger_full_render)
        bind(self, "offset_y", UIRenderGroup.trigger_full_render)

        self.rect = LBWH(0, 0, child.width, child.height)

    @property
    def child(self) -> UIWidget | None:
        """The wrapped child widget."""
        return self.children[0] if self.children else None

    def add(self, child: W, **kwargs) -> W:
        if len(self.children) >= 1:
            raise ValueError("UIRenderGroup only supports a single child.")

        super().add(child, **kwargs)
        return child

    def do_layout(self):
        """Place the child at (0, 0) filling the group.

        The child subtree uses a local coordinate system, which is mapped
        into the parent surface when the cached surface is drawn.
        """
        child = self.child
        if child:
            child.rect = LBWH(0, 0, self.content_width, self.content_height)

    def _update_surface_size(self) -> bool:
        """Resize the internal surface to the group's content size.

        Returns:
            True if the surface was resized (content is lost in that case).
        """
        size = (max(1, int(self.content_width)), max(1, int(self.content_height)))
        if self._surface.size != size:
            self._surface.resize(size=size, pixel_ratio=self._surface.pixel_ratio)
            return True
        return False

    def _subtree_requires_render(self) -> bool:
        """Check if any visible widget in the child subtree requests a render."""
        stack: list[UIWidget] = list(self.children)
        while stack:
            widget = stack.pop()
            if not widget.visible:
                continue
            if widget._requires_render:
                return True
            stack.extend(widget.children)
        return False

    def _do_render(self, surface: Surface, force: bool = False) -> bool:
        if not self.visible:
            return False

        resized = self._update_surface_size()

        requires_draw = force or self._requires_render
        self._requires_render = False

        # Only re-render the subtree into the internal surface when a child
        # requests it. A forced render from outside (e.g. a cleared parent
        # surface) does not invalidate the cached surface content.
        if resized or self._subtree_requires_render():
            with self._surface.activate():
                self._surface.clear(self._bg_color or TRANSPARENT_BLACK)
                for child in self.children:
                    child._do_render(self._surface, force=True)
            requires_draw = True

        if requires_draw:
            # draw without limiting the viewport to the widget's rect,
            # so rotation and scaling may extend beyond the allocated space
            surface.limit(None)
            rect = self.content_rect
            self._surface.draw(
                position=(rect.left + self.offset_x, rect.bottom + self.offset_y),
                angle=self.angle,
                anchor=self.anchor,
                alpha=int(self.alpha),
                scale=self.scale,
                color=self.tint,
            )
            return True

        return False

    def _dispatch_event_to_child(self, child: UIWidget, event: UIEvent) -> bool | None:
        """Convert mouse events into the child's local coordinate system.

        Only events passed to the child subtree are transformed; the group
        itself (e.g. hover or click handling of an interactive subclass)
        keeps working with the untransformed event in parent space.
        """
        if isinstance(event, UIMouseEvent):
            transformed = self._transform_mouse_event(event)
            if transformed is None:
                return EVENT_UNHANDLED
            event = transformed
        return super()._dispatch_event_to_child(child, event)

    def _scale_xy(self) -> tuple[float, float]:
        scale = self.scale
        if isinstance(scale, (int, float)):
            return float(scale), float(scale)
        return float(scale[0]), float(scale[1])

    def _transform_mouse_event(self, event: UIMouseEvent) -> UIMouseEvent | None:
        """Return a copy of the event with coordinates in local space.

        Applies the inverse of the visual transformation
        (translation, rotation and scaling around ``anchor``).
        Returns None if the transformation is not invertible (scale of 0).
        """
        sx, sy = self._scale_xy()
        if sx == 0 or sy == 0:
            return None

        x, y = self._to_local(event.x, event.y)
        changes: dict[str, int] = {"x": round(x), "y": round(y)}

        if isinstance(event, (UIMouseMovementEvent, UIMouseDragEvent)):
            dx, dy = self._inverse_rotate_scale(event.dx, event.dy)
            changes["dx"] = round(dx)
            changes["dy"] = round(dy)

        return replace(event, **changes)

    def _to_local(self, x: float, y: float) -> tuple[float, float]:
        """Map a point from parent coordinates into local (child) coordinates."""
        rect = self.content_rect
        ax, ay = self.anchor or (rect.width / 2, rect.height / 2)

        # translate into local coordinates, relative to the anchor,
        # compensating for the visual offset applied when drawing
        vx = x - rect.left - self.offset_x - ax
        vy = y - rect.bottom - self.offset_y - ay

        vx, vy = self._inverse_rotate_scale(vx, vy)
        return vx + ax, vy + ay

    def _inverse_rotate_scale(self, vx: float, vy: float) -> tuple[float, float]:
        """Apply the inverse of the rotation and scale to a vector.

        The surface is drawn with scale applied first, then rotation,
        so the inverse rotates back first and then scales back.
        """
        a = radians(self.angle)
        c, s = cos(a), sin(a)
        rx = vx * c + vy * s
        ry = -vx * s + vy * c

        sx, sy = self._scale_xy()
        return rx / sx, ry / sy


class UIAnimatedGroup(UIRenderGroup, UIInteractiveWidget):
    """An interactive :class:`UIRenderGroup` which can animate itself.

    This is the main entry point for GUI animations. It combines

    - the cached rendering and transform properties of :class:`UIRenderGroup`
      (``scale``, ``angle``, ``alpha``, ``offset_x``, ``offset_y``, ``tint``),
    - the interactive states of :class:`~arcade.gui.UIInteractiveWidget`
      (``hovered``, ``pressed``, ``disabled`` and the ``on_click`` event),
    - and the animation API (:meth:`animate`, :meth:`add_transition`).

    Hover and click hit-testing runs against the group's untransformed rect
    in parent space, so the trigger zone stays stable while the visuals are
    scaled or rotated. The child subtree still receives mouse events
    transformed into its local coordinate system.

    React to state changes by binding to the group's properties:

    .. code-block:: python

        group = UIAnimatedGroup(child=UIFlatButton(text="Play"))

        def on_hover_change():
            if group.hovered:
                group.animate(scale=1.08, duration=0.15, ease=Easing.BACK_OUT)
            else:
                group.animate(scale=1.0, duration=0.15)

        bind(group, "hovered", on_hover_change)

    Args:
        child: The wrapped widget.
        **kwargs: Passed on, e.g. ``interaction_buttons`` of
            :class:`~arcade.gui.UIInteractiveWidget`.
    """

    def __init__(self, *, child: UIWidget, **kwargs):
        super().__init__(child=child, **kwargs)
        self._transitions: list[TransitionBase] = []

    def on_event(self, event: UIEvent) -> bool | None:
        # tick here instead of in an on_update handler, so subclasses
        # overriding on_update without calling super() do not break animations
        if isinstance(event, UIOnUpdateEvent):
            self._update_transitions(event.dt)
        return super().on_event(event)

    def _update_transitions(self, dt: float) -> None:
        for transition in self._transitions[:]:
            transition.tick(self, dt)

            if transition.finished:
                self._transitions.remove(transition)

    def add_transition(self, transition: T) -> T:
        """Add a low level transition, which is ticked with update time.

        Most code should prefer :meth:`animate`.
        """
        self._transitions.append(transition)
        return transition

    def clear_transitions(self):
        """Remove all transitions from this group.

        Finished transitions are removed automatically.

        This also stops all running animations, including animations of other
        code. Prefer :meth:`Animation.stop` or starting a new animation for
        the same properties, which takes them over automatically.
        """
        self._transitions.clear()

    def animate(
        self,
        *,
        duration: float = 0.3,
        ease: EasingFunction = Easing.LINEAR,
        delay: float = 0.0,
        repeat: int | bool = 0,
        yoyo: bool = False,
        **properties: Any,
    ) -> Animation:
        """Animate properties of this group over time.

        .. code-block:: python

            group.animate(scale=1.08, duration=0.15, ease=Easing.BACK_OUT)
            group.animate(alpha=0, duration=0.5).then(duration=0.1).on_finish(arcade.exit)
            group.animate(scale=1.05, duration=0.6, ease=Easing.SINE, repeat=True, yoyo=True)

        Start values are read when the animation starts.
        Starting a new animation takes over its properties from other running
        animations, which keep animating their remaining properties.

        The transform properties (``scale``, ``angle``, ``alpha``,
        ``offset_x``, ``offset_y``, ``tint``) animate the wrapped subtree
        visually, without affecting layouting.

        Args:
            duration: Duration of the animation in seconds.
            ease: Easing function, see :class:`arcade.anim.Easing`.
            delay: Seconds to wait before the animation starts.
            repeat: How often to repeat the animation, ``True`` repeats forever.
            yoyo: If True, the animation plays backwards to its start values
                before it finishes (or repeats).
            **properties: Attribute names mapped to target values,
                e.g. ``scale=1.08``. Values wrapped in
                :func:`~arcade.gui.experimental.rel` are relative to the
                current value.

        Returns:
            The running :class:`~arcade.gui.experimental.Animation`, which can
            be extended with ``.then(...)``, observed with ``.on_finish(...)``
            and cancelled with ``.stop()``.
        """
        return self.add_transition(
            Animation(
                duration=duration,
                ease=ease,
                delay=delay,
                repeat=repeat,
                yoyo=yoyo,
                **properties,
            )
        )
