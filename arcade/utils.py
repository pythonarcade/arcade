"""
Various utility functions.

IMPORTANT: These should be standalone and not rely on any Arcade imports
"""

import platform
import sys
from collections.abc import MutableSequence
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Generator, Generic, Iterable, Sequence, Type, TypeVar

from arcade.types import AsFloat, Point2

__all__ = [
    "as_type",
    "type_name",
    "copy_dunders_unimplemented",
    "is_iterable",
    "is_nonstr_iterable",
    "is_str_or_noniterable",
    "grow_sequence",
    "is_raspberry_pi",
    "get_raspberry_pi_info",
]

# Since this module forbids importing from the rest of
# Arcade, we make our own local type variables.
_T = TypeVar("_T")
_TType = TypeVar("_TType", bound=Type)


class Chain(Generic[_T]):
    """A reusable OOP version of :py:class:`itertools.chain`.

    In some cases (physics engines), we need to iterate over multiple
    sequences of objects repeatedly. This class provides a way to do so
    which:

    * Is non-exhausting
    * Avoids copying all items into one joined list

    Arguments:
        components: The sequences of items to join.
    """

    def __init__(self, *components: Sequence[_T]):
        self.components: list[Sequence[_T]] = list(components)

    def __iter__(self) -> Generator[_T, None, None]:
        for item in chain.from_iterable(self.components):
            yield item


def as_type(item: Any) -> type:
    """If item is not a type, return its type. Otherwise, return item as-is.

    Args:
        item: A :py:class:`type` or instance of one.
    """
    if isinstance(item, type):
        return item
    else:
        return item.__class__


def type_name(item: Any) -> str:
    """Get the name of item if it's a type or the name of its type if it's an instance.

    This is meant to help shorten debugging-related code and developer
    utilities. It isn't meant to be a performant tool.

    Args:
         item: A :py:class:`type` or an instance of one.
    """
    if isinstance(item, type):
        return item.__name__
    else:
        return item.__class__.__name__


def is_iterable(item: Any) -> bool:
    """Use :py:func:`iter` to infer whether ``item`` is iterable.

    .. tip:: An empty iterable still counts as an iterable.

    This relies on the following:

    #. Python's :py:func:`iter` raises a :py:class:`TypeError` if
       ``item`` is not iterable
    #. try/catch blocks are fast

    If you are still concerned about performance, you may want to inline
    the contents of this function locally since function calls may have
    more overhead than try/catch blocks on your Python version.

    Args:
         item:
            An object to pass to the built-in :py:func:`iter` function.

    Returns:
        ``True`` if the item appears to be iterable.
    """
    try:
        _ = iter(item)
        return True
    except TypeError:
        return False


def is_nonstr_iterable(item: Any) -> bool:
    """``True`` if ``item`` is an iterable other than a :py:class:`str`.

    In addition to calling this function ``if`` and ``elif`` statements,
    you can also pass it as an argument to other functions. These include:

    * The :py:func:`.grow_sequence` utility function
    * Python's built-in filter function

    .. note:: This is the opposite of :py:func:`is_str_or_noniterable`.

    Args:
         item: Any object.

    Returns:
        Whether ``item`` is a non-string iterable.
    """
    return not isinstance(item, str) and is_iterable(item)


def is_str_or_noniterable(item: Any) -> bool:
    """``True`` if ``item`` is a string or non-iterable.

    In addition to calling this function in ``if`` and ``elif`` statements,
    you can also pass it as an argument to other functions. These include:

    * The :py:func:`.grow_sequence` utility function
    * Python's built-in :py:func:`filter` function

    .. note:: This is the opposite of :py:func:`is_str_or_noniterable`.

    Args:
        item: Any object.

    Returns:
        ``True`` if ``item`` is a :py:class:`str` or a non-iterable
        object.
    """
    return isinstance(item, str) or not is_iterable(item)


def grow_sequence(
    destination: MutableSequence[_T],
    source: _T | Iterable[_T],
    append_if: Callable[[_T | Iterable[_T]], bool] = is_str_or_noniterable,
) -> None:
    """Append when ``append_if(to_add)`` is ``True``, extend otherwise.

    If performance is critical, consider inlining this code. This function
    is meant as:

    * a companion to :py:data:`arcade.types.OneOrIterableOf`
    * an abbreviation for repetitive if-blocks in config and settings menus

    The default ``append_if`` value is the :py:func:`.is_str_or_noniterable`
    function in this module. You can pass any :py:func:`~typing.Callable`
    which returns:

    * ``True`` if we should :py:meth:`append <list.append>`
    * ``False`` if we should :py:meth:`extend <list.extend>`

    This includes both the :py:class:`callable` function and your own custom
    functions. For example:

    .. code-block:: python

       dest = []

       def _validate_and_choose(item) -> bool:
           \"\"\"Raises an exception if data is invalid or a bool if not.\"\"\"
           ...

       # Okay values
       grow_sequence(dest, MyType(), append_when=_validate_and_choose)
       grow_sequence(dest, [MyType(), MyType()], append_when=_validate_and_choose)

       # Raises an exception
       grow_sequence(dest, BadType(), append_when=_validate_and_choose)


    Args:
        destination:
            A :py:func:`list` or other :py:class:`~typing.MutableSequence`
            to append to or extend.
        source:
            A value source we'll use to grow the ``destination``
            sequence.
        append_if:
            A :py:func:`callable` which returns ``True`` when ``source``
            should be appended.
    """
    if append_if(source):
        destination.append(source)  # type: ignore
    else:
        destination.extend(source)  # type: ignore


def copy_dunders_unimplemented(decorated_type: _TType) -> _TType:
    """Decorator stubs dunders raising :py:class:`NotImplementedError`.

    Temp fixes https://github.com/pythonarcade/arcade/issues/2074 by
    stubbing the following instance methods:

    * :py:meth:`object.__copy__` (used by :py:func:`copy.copy`)
    * :py:meth:`object.__deepcopy__` (used by :py:func:`copy.deepcopy`)

    Example usage:

    .. code-block:: python

       import copy
       from arcade,utils import copy_dunders_unimplemented
       from arcade.hypothetical_module import HypotheticalNasty

       # Example usage
       @copy_dunders_unimplemented
       class CantCopy:
            def __init__(self, nasty_state: HypotheticalNasty):
                self.nasty_state = nasty_state

       instance = CantCopy(HypotheticalNasty())

       # These raise NotImplementedError
       this_line_raises = copy.deepcopy(instance)
       this_line_also_raises = copy.copy(instance)
    """

    def __copy__(self):  # noqa
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement __copy__, but"
            f"you may implement it on a custom subclass."
        )

    decorated_type.__copy__ = __copy__

    def __deepcopy__(self, memo):  # noqa
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement __deepcopy__,"
            f" but you may implement it on a custom subclass."
        )

    decorated_type.__deepcopy__ = __deepcopy__

    return decorated_type


def is_raspberry_pi() -> bool:
    """Determine if the host is a raspberry pi."""
    return get_raspberry_pi_info()[0]


def get_raspberry_pi_info() -> tuple[bool, str, str]:
    """
    Determine if the host is a raspberry pi with additional info.

    Returned tuple format is::

            bool (is host a raspi)
            str (architecture)
            str (model name)
    """
    # The platform for raspi should always be linux
    if not sys.platform == "linux":
        return False, "", ""

    # armv7l is raspi 32 bit
    # aarch64 is raspi 64 bit
    architecture = platform.machine()
    model_name = ""

    # Check for model info file
    MODEL_PATH = Path("/sys/firmware/devicetree/base/model")
    if MODEL_PATH.exists():
        try:
            model_name = MODEL_PATH.read_text()[:-1]
            if "raspberry pi" in model_name.lower():
                return True, architecture, model_name
        except Exception:
            pass

    return False, "", ""


def unpack_asfloat_or_point(value: AsFloat | Point2) -> Point2:
    """
    A utility method that converts a float or int into a Point2, or
    validates that an iterable is a Point2.

    .. note:: This should be inlined in hot code paths

    Args:
        value: The value to test.

    Returns:
        A Point2 that is either equal to value, or is equal to (value, value)
    """

    if isinstance(value, (float, int)):
        x = y = value
    else:
        try:
            x, y = value
        except ValueError:
            raise ValueError(
                "value must be a float, int, or tuple-like which unpacks as two float-like values"
            )
        except TypeError:
            raise TypeError(
                "value must be a float, int, or tuple-like unpacks as two float-like values"
            )

    return x, y
