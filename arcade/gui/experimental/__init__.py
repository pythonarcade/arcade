"""Contains experimental GUI elements.

The API of these components may change within minor version updates.
No Deprecation warnings are given for changes in this module.
"""

from arcade.gui.experimental.scroll_area import UIScrollArea
from arcade.gui.experimental.password_input import UIPasswordInput
from arcade.gui.experimental.animate import Animation, rel
from arcade.gui.experimental.group import UIRenderGroup, UIAnimatedGroup
from arcade.gui.experimental.transition import (
    TransitionBase,
    EventTransitionBase,
    TransitionAttr,
    TransitionAttrIncr,
    TransitionAttrSet,
    TransitionChain,
    TransitionParallel,
    TransitionDelay,
)

__all__ = [
    "UIScrollArea",
    "UIPasswordInput",
    "UIRenderGroup",
    "UIAnimatedGroup",
    "Animation",
    "rel",
    "TransitionBase",
    "EventTransitionBase",
    "TransitionAttr",
    "TransitionAttrIncr",
    "TransitionAttrSet",
    "TransitionChain",
    "TransitionParallel",
    "TransitionDelay",
]
