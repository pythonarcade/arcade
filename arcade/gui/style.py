from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypeVar, overload

from arcade.gui.property import DictProperty
from arcade.gui.widgets import UIWidget


@dataclass
class UIStyleBase:
    """
    Base class for styles to ensure a general interface and implement additional magic.

    Support dict like access syntax.

    A styled widget should own a dataclass, which subclasses this class
    """

    @overload
    def get(self, key, default: str) -> str: ...

    @overload
    def get(self, key, default: Any) -> Any: ...

    def get(self, key, default=None):
        return self[key] if key in self else default

    def __contains__(self, item):
        return hasattr(self, item)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


StyleRef = TypeVar("StyleRef", bound=UIStyleBase)


class UIStyledWidget(UIWidget, Generic[StyleRef]):
    # TODO detect StyleBase changes, so that style changes can trigger rendering.
    style: Mapping = DictProperty()  # type: ignore

    def __init__(self, *, style: Mapping[str, StyleRef], **kwargs):
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

    def get_current_style(self) -> StyleRef:
        """Return style based on any state of the widget"""
        return self.style.get(self.get_current_state(), None)
