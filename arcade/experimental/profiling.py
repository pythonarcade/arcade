"""
Simple experimental profiler. This api is not stable.
"""
import cProfile
import pstats
from io import StringIO
from contextlib import contextmanager


class Profiler:
    """
    A profiler that can measure the execution time within a section
    of your code.

    Examples::

        # Context manager
        profiler = Profiler()
        with profiler.enabled():
            # Code you want to measure
        profiler.print_stats()

        # Enable and disable manually
        profiler = Profiler()
        profiler.enable()
        # Code you want to measure
        profiler.disable()
        profiler.print_stats()

        The same profiler instance can be enabled multiple times
        to accumulate data.

    :param str sort_by: function sort order
    """
    def __init__(self, sort_by="tottime"):
        self._sort_by = sort_by
        self._profiler = cProfile.Profile()

    @contextmanager
    def enabled(self):
        self.enable()
        try:
            yield
        finally:
            self.disable()

    def enable(self):
        """Start/enable the profiler"""
        self._profiler.enable()

    def disable(self):
        """Stop/disable the profiler"""
        self._profiler.disable()

    def print_stats(self):
        stats = pstats.Stats(self._profiler).sort_stats(self._sort_by)
        stats.print_stats()

    def get_stats_string(self):
        strdata = StringIO()
        pstats.Stats(self._profiler, stream=strdata).sort_stats(self._sort_by)
        return strdata.getvalue()
