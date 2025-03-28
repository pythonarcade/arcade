from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, overload

from arcade.gui.property import DictProperty
from arcade.gui.widgets import UIWidget


@dataclass
class UIStyleBase:
    """Base class for styles to ensure a general interface and implement additional magic.

    Support dict like access syntax.

    A styled widget should own a dataclass, which subclasses this class
    """

    @overload
    def get(self, key, default: str) -> str: ...

    @overload
    def get(self, key, default: Any) -> Any: ...

    def get(self, key, default=None):
        """Get a value from the style, if not available return default."""
        return self[key] if key in self else default

    def __contains__(self, item):
        return hasattr(self, item)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


StyleRef = TypeVar("StyleRef", bound=UIStyleBase)


class UIStyledWidget(UIWidget, Generic[StyleRef]):
    """Baseclass for widgets to be styled.

    A styled widget should own a dataclass, which subclasses UIStyleBase.
    The style dict should contain the different states of the widget.

    The widget should implement py:method::`get_current_state()`,
    which should return the current state of the widget.

    Args:
        style: A mapping of states to styles
        **kwargs: passed to UIWidget

    """

    # TODO detect StyleBase changes, so that style changes can trigger rendering.
    style = DictProperty[str, StyleRef]()

    def __init__(self, *, style: dict[str, StyleRef], **kwargs):
        self.style = style
        super().__init__(**kwargs)

    @abstractmethod
    def get_current_state(self) -> str:
        """
        Return the current state of the widget. These should be contained in the style dict.

        Well known states:
        - normal
        - hover
        - press
        - disabled
        """
        pass

    def get_current_style(self) -> StyleRef | None:
        """Return style based on any state of the widget"""
        return self.style.get(self.get_current_state(), None)
