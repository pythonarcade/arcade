"""Prevents import issues.

If an :py:mod:`arcade.types` submodule attempts to run
``from arcade.types import AsFloat``, it could cause issues with
circular imports or partially initialized modules.
"""

from __future__ import annotations

from typing import Union

#: 1. Makes pyright happier while also telling readers
#: 2. Tells readers we're converting any ints to floats
AsFloat = Union[float, int]

__all__ = ["AsFloat"]
