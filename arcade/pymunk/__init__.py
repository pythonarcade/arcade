"""
All of the pymunk functionality used by arcade. This __init__ will optionally
switch between dud defintions and the real classes based on if pymunk is importable.

To gain access to these objects pymunk must be imported before arcade is imported.
"""

import sys

print(sys.modules)
if "pymunk" in sys.modules:
    # Pymunk has been imported so its safe to present the real objects
    from .mixins import PyMunk, PymunkMixin  # type: ignore
    from .engines import PymunkPhysicsObject, PymunkPhysicsEngine, PymunkException  # type: ignore
    from .hitbox import PymunkHitBoxAlgorithm  # type: ignore
else:
    # Pymunk has not been imported so it is unsafe to present the real objectsS
    from .mixins_dud import PyMunk, PymunkMixin  # type: ignore
    from .engines_dud import PymunkPhysicsObject, PymunkPhysicsEngine, PymunkException  # type: ignore
    from .hitbox_dud import PymunkHitBoxAlgorithm  # type: ignore


__all__ = (
    "PyMunk",
    "PymunkMixin",
    "PymunkPhysicsObject",
    "PymunkPhysicsEngine",
    "PymunkException",
    "PymunkHitBoxAlgorithm",
)
