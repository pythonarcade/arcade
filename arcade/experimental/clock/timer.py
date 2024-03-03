import weakref
from typing import Callable,List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from arcade.experimental.clock.clock import Clock


class Timer:
    """
    A basic timer class which can be used to 'set and forget' a method call.
    If you simply want to know how long since an event has elapsed you can
    interact with arcade's clocks.

    Timers overlap heavily with Pyglet's own clock system. If you want to
    schedule a function that is irrespective of the arcade's clock time then
    using Pyglet's clock may better suit your needs.

    Arcade's clocks assure simultaneous timers. If two bullets are created on
    the same frame they will both treat it as though they were spawned at the
    same time. This is not true for events created by Pyglet's clocks.

    The timer makes no implicit expectations about the flow of time. Setting
    a negative duration will make the timer expect the flow of time to be
    reversed. If time is moving in the opposite direction to what the timer
    expects it will not be active.

    If you want to get information from the timer and pass it to the function
    you can. The possible options are:
        'duration' which gives the duration of the timer
        'elapsed' which gives the currently elapsed time of the parent clock
        'tick_count' which gives the tick_count of the parent clock
        'tick_speed' which gives the tick speed of the parent clock
        'timer' which gives the timer making the callback
        'clock' which gives the parent of the timer making the callback
    simply add the option as a kwarg equal to none. ensure your callback function
    accepts any you want to use as a kwarg.
    """

    def __init__(self, duration: float, parent: "Clock", callback: Callable, *args,
                 delay: float = 0.0,
                 reusable: bool = False,
                 **kwargs
                 ):
        self._parent: "Clock" = parent

        self._duration: float = duration
        self._delay: float = delay

        self._start_time: float = parent.elapsed + delay

        self._complete: bool = False

        self._callback: Optional[Callable] = weakref.proxy(callback)
        self._args: List[Any] = list(args)
        self._kwargs: Dict[str, Any] = kwargs or dict()

        self.reusable: bool = reusable

    def kill(self):
        self.free()
        self._start_time = 0.0

        if not self.reusable:
            self._duration = 0.0
            self._delay = 0.0
            self._callback = None
            self._args = list()
            self._kwargs = dict()

    def check(self, auto_kill: bool = True, auto_call: bool = True):
        if not self._parent or not self._duration or not self.active:
            return

        self._complete = abs(self._duration) <= abs(self._parent.time_since(self._start_time))

        if not self._complete:
            return

        if auto_call:
            self.call()

        if auto_kill:
            self.kill()

    def reuse(self,
              new_parent: "Clock",
              new_duration: Optional[float] = None,
              new_delay: Optional[float] = None,
              ):
        new_parent.add_timer(self)

        self._duration = new_duration or self._duration
        self._delay = new_delay or self._delay

        self._start_time = self._parent.elapsed + self._delay

    def arg_update(self, arg_index: int, value: Any):
        self._args[arg_index] = value

    def args_override(self, *args):
        self._args = args

    def kwarg_update(self, **kwargs):
        self._kwargs = self._kwargs | kwargs

    def kwarg_override(self, **kwargs):
        self._kwargs = kwargs

    def call(self, force_complete: bool = True):
        if force_complete and not self._complete:
            raise ValueError("The timer has not completed, but force_complete is active")

        if not self._callback:
            return

        if 'duration' == self._kwargs and self._kwargs['duration'] is None:
            self._kwargs['duration'] = self._duration
        if 'timer' == self._kwargs and self._kwargs['timer'] is None:
            self._kwargs['timer'] = self

        if self._parent:
            if 'elapsed' in self._kwargs and self._kwargs['elapsed'] is None:
                self._kwargs['elapsed'] = self._parent.elapsed
            if 'tick_count' in self._kwargs and self._kwargs['tick_count'] is None:
                self._kwargs['tick_count'] = self._parent.tick_count
            if 'tick_speed' in self._kwargs and self._kwargs['tick_speed'] is None:
                self._kwargs['tick_speed'] = self._parent.tick_speed
            if 'clock' in self._kwargs and self._kwargs['clock'] is None:
                self._kwargs['clock'] = self._parent

        self._callback(*self._args, **self._kwargs)

    def free(self):
        if self._parent:
            self._parent.pop_timer(self)

    @property
    def complete(self):
        return self._complete

    @property
    def active(self) -> bool:
        if not self._parent or not self._duration or self._complete:
            return False

        if self._duration < 0:
            return self._parent.elapsed <= self._start_time
        else:
            return self._start_time <= self._parent.elapsed

    @property
    def percentage(self):
        if not self.active:
            return 0.0

        return self._parent.time_since(self._start_time) / self._duration
