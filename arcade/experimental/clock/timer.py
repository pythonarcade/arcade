from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arcade.experimental.clock.clock import Clock


class Timer:
    """
    A basic timer class which can be used to 'set and forget' a method call.
    If you simply want to know how long since an event has elapsed you can
    interact with arcade's clocks.

    Timers overlap heavily with pyglet's own clock system. If you want to
    schedule a function that is irrespective of the arcade's clock time then
    using pyglet's clock may better suit your needs.

    Arcade's clocks assure simultaneous timers. If two bullets are created on
    the same frame they will both treat it as though they were spawned at the
    same time. This is not true for events created by Pyglet's clocks.
    """

    @property
    def complete(self):
        return False

    def kill(self, no_call: bool = False):
        pass

    def check(self, auto_kill: bool = True):
        pass

    def arg_override(self, *args):
        pass

    def kwarg_override(self, **kwargs):
        pass
