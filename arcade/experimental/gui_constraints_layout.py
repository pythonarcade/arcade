"""
Why a ConstraintsLayout?

The current layout system is very static, it is not possible to create dynamic layouts.




"""

from __future__ import annotations

from abc import abstractmethod
from typing import Callable

from arcade import easing
from arcade.gui import UILayout, UIWidget
from arcade.gui.widgets import W


class Constraint:
    """Constraint is a callable that returns a value, which can be used to set an UIWidgets attribute.

    Constraints also support lambda expressions, which can be used to create simple context aware constraints.
    """

    def __call__(self) -> int:
        return self.eval()

    def on_update(self, dt_seconds: float):
        pass

    @abstractmethod
    def eval(self) -> int:
        pass

    @staticmethod
    def ensure_constraint(c) -> "Constraint":
        if isinstance(c, Constraint):
            return c
        elif isinstance(c, Callable):
            return _LambdaConstraint(c)
        else:
            return ValueConstraint(c)

    def __add__(self, other) -> "Constraint":
        other = Constraint.ensure_constraint(other)
        return _CombinedConstraint(lambda: self() + other(), self, other)

    def __sub__(self, other) -> "Constraint":
        other = Constraint.ensure_constraint(other)
        return _CombinedConstraint(lambda: self() - other(), self, other)

    def __mul__(self, other) -> "Constraint":
        other = Constraint.ensure_constraint(other)
        return _CombinedConstraint(lambda: self() * other(), self, other)

    def __truediv__(self, other) -> "Constraint":
        other = Constraint.ensure_constraint(other)
        return _CombinedConstraint(lambda: self() / other(), self, other)

    def __floordiv__(self, other) -> "Constraint":
        other = Constraint.ensure_constraint(other)
        return _CombinedConstraint(lambda: self() // other(), self, other)


class TimedConstraint(Constraint):
    """A constraint that changes over time, it provides a self.t
    attribute, which is updated on every update call.

    Returns self.t as value.
    You can also provide a function, which is called with the current time as argument.
    """

    def __init__(self, func: Callable = None):
        super().__init__()
        self.t = 0
        self.func = func

    def on_update(self, dt_seconds: float):
        self.t += dt_seconds

    def eval(self) -> int:
        if self.func:
            return self.func(self.t)

        return self.t


class _LambdaConstraint(Constraint):
    """A constraint returning a value relative to the given widgets attribute"""

    def __init__(self, func):
        self.func = func

    def eval(self) -> int:
        return self.func()


class _CombinedConstraint(Constraint):
    """A Constraint holding two constraints, passing the update method to both of them."""

    def __init__(self, func, *constraints: Constraint):
        self.func = func
        self.constraints = constraints

    def on_update(self, dt_seconds: float):
        for c in self.constraints:
            c.on_update(dt_seconds)

    def eval(self) -> int:
        return self.func()


class EasingConstraint(TimedConstraint):
    """A constraint that uses an easing function to change its value over time.

    :param seconds: time at which the value reaches 1
    :param ease_function: easing function, defaults to linear
    """

    def __init__(self, *, seconds: float, ease_function: Callable = None):
        super().__init__()
        self.end_time = seconds
        self.ease_function = ease_function or easing.linear

    def eval(self) -> int:
        return self.ease_function(min(self.t / self.end_time, 1))


class EasingValueConstraint(TimedConstraint):
    """A constraint that uses an easing function to change its value over time.

    :param seconds: time at which the value reaches 1
    :param ease_function: easing function, defaults to linear
    """

    def __init__(
        self, *, start_value, end_value, seconds: float, ease_function: Callable = None
    ):
        super().__init__()
        self.start_value = Constraint.ensure_constraint(start_value)
        self.end_value = Constraint.ensure_constraint(end_value)
        self.end_time = seconds
        self.ease_function = ease_function or easing.linear

    def eval(self) -> int:
        start = self.start_value()
        end = self.end_value()
        return start + (end - start) * self.ease_function(
            min(self.t / self.end_time, 1)
        )


class ValueConstraint(Constraint):
    """A constraint returning a constant value"""

    def __init__(self, value: int):
        self.value = value

    def eval(self) -> int:
        return self.value


class RelativeConstraint(Constraint):
    """A constraint returning a value relative to the given widgets attribute"""

    def __init__(
        self, widget: W, attribute: str, *, factor: float = 1.0, offset: int = 0
    ):
        self.widget = widget
        self.attribute = attribute
        self.factor = factor
        self.offset = offset

    def eval(self) -> int:
        return getattr(self.widget, self.attribute) * self.factor + self.offset


class UIWidgetAttrMixin(UIWidget):
    """provides setter for UIWidget attributes, which are currently missing, this is a workaround.

    Provides property setters for the following attributes:
    * width
    * height
    * top
    * bottom
    * left
    * right
    * center_x
    * center_y
    """

    @UIWidget.width.setter
    def width(self, value):
        self.rect = self.rect.resize(width=value)

    @UIWidget.height.setter
    def height(self, value):
        self.rect = self.rect.resize(height=value)

    @UIWidget.top.setter
    def top(self, value):
        self.rect = self.rect.align_top(value)

    @UIWidget.bottom.setter
    def bottom(self, value):
        self.rect = self.rect.align_bottom(value)

    @UIWidget.left.setter
    def left(self, value):
        self.rect = self.rect.align_left(value)

    @UIWidget.right.setter
    def right(self, value):
        self.rect = self.rect.align_right(value)

    @UIWidget.center_x.setter
    def center_x(self, value):
        self.rect = self.rect.align_center_x(value)

    @UIWidget.center_y.setter
    def center_y(self, value):
        self.rect = self.rect.align_center_y(value)


class UIConstraintsLayout(UILayout):
    """ConstraintsLayout is a layout that allows to set widgets attributes to constraints instead of values.

    This enables the creation of dynamic layouts.

    ⚡️ Against normal conventions (right now), this layout is able to place widgets out-side of its own rect.
    """

    def __init__(self, **kwargs):
        super().__init__(size_hint=(1, 1), **kwargs)

    def add(self, child: W, **kwargs: Constraint | Callable | int) -> W:
        # ensure constraints
        for a, c in kwargs.items():
            kwargs[a] = Constraint.ensure_constraint(c)

        return super().add(child, **kwargs)

    def on_update(self, dt):
        for child, data in self._children:
            for _, constraint in data.items():
                constraint.on_update(dt)

    def do_layout(self):
        for child, data in self._children:
            child: UIWidget

            for attr, constraint in data.items():
                if hasattr(child, attr):
                    setattr(child, attr, constraint())

                else:
                    raise AttributeError(f"Widget {child} has no attribute {attr}")
