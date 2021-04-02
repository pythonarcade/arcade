import warnings

# Deprecated
warnings.warn(
    "arcade.gui.ui_style is deprecated, import from arcade.gui.style.",
    category=DeprecationWarning,
)

from arcade.gui.style import UIStyle

__all__ = ["UIStyle"]
