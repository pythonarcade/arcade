"""Prevents import issues.

If an :py:mod:`arcade.types` submodule attempts to run
``from arcade.types import AsFloat``, it could cause issues with
circular imports or partially initialized modules.
"""

#: A float or an int. Arcade accepts either where it uses this type,
#: and works with the value as a float.
AsFloat = float | int

__all__ = ["AsFloat"]
