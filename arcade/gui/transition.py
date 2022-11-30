import math
from abc import ABC, abstractmethod
from typing import Callable, Any, Optional, List, TypeVar

from pyglet.event import EventDispatcher

T = TypeVar("T", bound="TransitionBase")


class EaseFunctions:
    @staticmethod
    def linear(x: float):
        return x

    @staticmethod
    def sine(x: float):
        return 1 - math.cos((x * math.pi) / 2)


class TransitionBase(ABC):
    @abstractmethod
    def tick(self, subject, dt) -> float:
        """
        Update

        :return: dt, which is not consumed
        """
        pass

    @property
    @abstractmethod
    def finished(self) -> bool:
        raise NotImplementedError()

    def __add__(self, other):
        return TransitionChain(self, other)

    def __or__(self, other):
        return TransitionParallel(self, other)


class EventTransitionBase(TransitionBase, EventDispatcher):
    """
    Extension of TransitionBase, providing hooks via

    - on_tick(subject, progress: float)
    - on_finish(subject)

    :param duration: Duration of the transition in seconds
    :param delay: Start transition after x seconds
    """

    def __init__(
        self,
        *,
        duration: float,
        delay=0.0,
    ):
        self._duration = duration
        self._elapsed = -delay

        self.register_event_type("on_tick")
        self.register_event_type("on_finish")

    def tick(self, subject, dt) -> float:
        self._elapsed += dt
        if self._elapsed >= 0:
            progress = min(self._elapsed / self._duration, 1) if self._duration else 1
            self.dispatch_event("on_tick", subject, progress)

        if self.finished:
            self.dispatch_event("on_finish", subject)

        return max(0.0, self._elapsed - self._duration)

    def on_tick(self, subject, progress):
        pass

    def on_finish(self, subject):
        pass

    @property
    def finished(self):
        return self._elapsed >= self._duration


class TransitionDelay(EventTransitionBase):
    def __init__(self, duration: float):
        super().__init__(duration=duration)


class TransitionAttr(EventTransitionBase):
    """
    Changes an attribute over time.

    :param start: start value, if None, the subjects value is read via `getattr`
    :param end: target value
    :param attribute: attribute to set
    :param duration: Duration of the transition in seconds
    :param ease_function:
    :param delay: Start transition after x seconds
    :param mutation_function: function to be used to set new value
    """

    def __init__(
        self,
        *,
        end,
        attribute,
        duration: float,
        start=None,
        ease_function=EaseFunctions.linear,
        delay=0.0,
        mutation_function: Callable[[Any, str, float], None] = setattr,
    ):
        super().__init__(duration=duration, delay=delay)
        self._start: Optional[float] = start
        self._end = end
        self._attribute = attribute

        self._ease_function = ease_function
        self._mutation_function = mutation_function

    def on_tick(self, subject, progress):
        if self._start is None:
            self._start = getattr(subject, self._attribute)

        factor = self._ease_function(progress)
        new_value = self._start + (self._end - self._start) * factor

        self._mutation_function(subject, self._attribute, new_value)


class TransitionAttrIncr(TransitionAttr):
    """
    Changes an attribute over time.

    :param increment: difference the value should be changed over time (can be negative)
    :param attribute: attribute to set
    :param duration: Duration of the transition in seconds
    :param ease_function:
    :param delay: Start transition after x seconds
    :param mutation_function: function to be used to set new value
    """

    def __init__(
        self,
        *,
        increment: float,
        attribute,
        duration: float,
        ease_function=EaseFunctions.linear,
        delay=0.0,
        mutation_function: Callable[[Any, str, float], None] = setattr,
    ):
        super().__init__(end=increment, attribute=attribute, duration=duration, delay=delay)
        self._attribute = attribute

        self._ease_function = ease_function
        self._mutation_function = mutation_function

    def on_tick(self, subject, progress):
        if self._start is None:
            self._start = getattr(subject, self._attribute)
            self._end += self._start

        factor = self._ease_function(progress)
        new_value = self._start + (self._end - self._start) * factor

        self._mutation_function(subject, self._attribute, new_value)


class TransitionAttrSet(EventTransitionBase):
    """
    Set the attribute when expired.

    :param value: value to set
    :param attribute: attribute to set
    :param duration: Duration of the transition in seconds
    """

    def __init__(
        self,
        *,
        value: float,
        attribute,
        duration: float,
        mutation_function=setattr
    ):
        super().__init__(duration=duration)
        self._attribute = attribute
        self._value = value
        self._mutation_function = mutation_function

    def on_finish(self, subject):
        setattr(subject, self._attribute, self._value)


class TransitionParallel(TransitionBase):
    """
    A transition assembled by multiple transitions.
    Executing them in parallel.
    """

    def __init__(self, *transactions: TransitionBase):
        super().__init__()
        self._transitions: List[TransitionBase] = list(transactions)

    def add(self, transition: T) -> T:
        self._transitions.append(transition)
        return transition

    def tick(self, subject, dt):
        remaining_dt = dt

        for transition in self._transitions[:]:

            r = transition.tick(subject, dt)
            remaining_dt = min(remaining_dt, r)

            if transition.finished:
                self._transitions.remove(transition)

        return remaining_dt

    @property
    def finished(self) -> bool:
        return not self._transitions


class TransitionChain(TransitionBase):
    """
    A transition assembled by multiple transitions.
    Executing them sequential.
    """

    def __init__(self, *transactions: TransitionBase):
        super().__init__()
        self._transitions: List[TransitionBase] = list(transactions)

    def add(self, transition: T) -> T:
        self._transitions.append(transition)
        return transition

    def tick(self, subject, dt):
        while dt and not self.finished:
            transition = self._transitions[0]
            dt = transition.tick(subject, dt)

            if transition.finished:
                self._transitions.pop(0)

        return min(0.0, dt)

    @property
    def finished(self) -> bool:
        return not self._transitions
