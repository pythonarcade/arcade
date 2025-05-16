"""Prevents import issues.

If an :py:mod:`arcade.types` submodule attempts to run
``from arcade.types import AsFloat``, it could cause issues with
circular imports or partially initialized modules.
"""

#: 1. Makes pyright happier while also telling readers
#: 2. Tells readers we're converting any ints to floats
AsFloat = float | int

__all__ = ["AsFloat"]
