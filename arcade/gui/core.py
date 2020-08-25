import typing
from typing import Optional, Set, Any
from uuid import uuid4

import arcade
from arcade.gui.ui_style import UIStyle

if typing.TYPE_CHECKING:
    from arcade.gui import UIManager

MOUSE_PRESS = 'MOUSE_PRESS'
MOUSE_RELEASE = 'MOUSE_RELEASE'
MOUSE_SCROLL = 'MOUSE_SCROLL'
MOUSE_MOTION = 'MOUSE_MOTION'
KEY_PRESS = 'KEY_PRESS'
KEY_RELEASE = 'KEY_RELEASE'

TEXT_INPUT = 'TEXT_INPUT'
TEXT_MOTION = 'TEXT_MOTION'
TEXT_MOTION_SELECTION = 'TEXT_MOTION_SELECTION'


class UIEvent:
    """
    Represents an interaction with the gui.
    """

    def __init__(self, type: str, **kwargs):
        """
        :param type: Type of the event, like :py:attr:`arcade.gui.MOUSE_PRESS` :py:attr:`arcade.gui.KEY_PRESS`
        :param kwargs: Data of the event
        """
        self.type = type
        self.data = kwargs

    def get(self, key: str) -> Any:
        """
        Retrieve value for given key

        :param str key
        """
        return self.data.get(key)

    def __repr__(self):
        return ' '.join([f'{self.type} ', *[f'{key}={value}' for key, value in self.data.items()]])


class UIElement(arcade.Sprite):
    """
    Base class for all UI elements.
    Implements :py:class:`arcade.Sprite`, requires a texture to be set in :py:meth:`arcade.gui.UIElement.render()`

    :py:class:`arcade.gui.UIElement` contains an id, which can be used to retrieve it from :py:class:`arcade.gui.UIManager`

    Holds a reference to a :py:class:`arcade.gui.UIStyle`, resolving values depending on the
    :py:attr:`UIElement().id`, :py:attr:`UIElement().style_classes`, and element specific style attributes.
    """

    def __init__(self,
                 center_x=0,
                 center_y=0,
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
        super().__init__()
        # ID for this element, to search in view by id or identify this element from an event
        self.__id = id
        self.mng: Optional['UIManager'] = None

        # unique id, to overwrite style for exactly this element, DONT CHANGE THIS LATER
        self.__style_id = str(uuid4())
        self.style_classes = ['globals']
        self._style: UIStyle = style if style else UIStyle.default_style()
        self._style.push_handlers(self.on_style_change)

        # what do we need to look like a proper arcade.Sprite
        # self.texture <- subclass
        # self.width/height <- subclass
        self.center_x = center_x
        self.center_y = center_y

    def __repr__(self):
        return f'UIElement({self.id if self.id else self.__style_id})'

    @property
    def id(self) -> Optional[str]:
        """
        You can set id on creation, but it can't be modify later
        """
        return self.__id

    @id.setter
    def id(self, value):
        if len(self.sprite_lists) > 0:
            raise UIException('Setting id, after adding to a UIManager, is to late!')

        self.__id = value

    @property
    def style(self) -> UIStyle:
        """
        :return: Referenced :py:class:`arcade.gui.UIStyle`
        """
        return self._style

    def set_style_attrs(self, **kwargs):
        """
        Sets a custom style attribute for this UIElement
        The value will be returned unparsed (like given)
        Setting an attribute to None will remove the overwrite, defaults will apply

        :param kwargs: key-value pairs
        """
        self._style.set_class_attrs(self.__style_id, **kwargs)

    def _lookup_classes(self):
        return [*self.style_classes, self.id, self.__style_id]

    def style_attr(self, key, default=None):
        """
        Resolve a style attribute.

        :param key: Attribute key
        :param default: default return if not found.
        :return: Attribute value or default value if attribute key was not found.
        """
        value = self._style.get_attr(self._lookup_classes(), key)

        return value if value else default

    def on_style_change(self, style_classes: Set[str]):
        """
        Callback which is used to trigger rerender.
        Normal subclasses don't have to overwrite this method.
        """
        if style_classes.intersection(set(self._lookup_classes())):
            self.render()

    def render(self):
        """
        Render and update textures, called on style change.
        Initially called while added to :py:class:`arcade.gui.UIManager`

        Has to be implemented by subclasses of :py:class:`arcade.gui.UIElement`.
        """
        raise NotImplementedError()

    def on_ui_event(self, event: UIEvent):
        """
        Callback for a :py:class:`arcade.gui.UIEvent`, triggered through pyglet.EventDispatcher

        :param UIEvent event: Dispatched event
        :return: If True is returned the dispatch will stop
        """
        pass

    def on_focus(self):
        """
        Callback if the element gets focused
        """
        pass

    def on_unfocus(self):
        """
        Callback if the element gets unfocused aka is not focused any more
        """
        pass

    def on_hover(self):
        """
        Callback if the element gets hovered
        """
        pass

    def on_unhover(self):
        """
        Callback if the element gets unhovered aka is not focused any more
        """
        pass


class UIException(Exception):
    """
    Abstract Exception within the UI.
    """
    pass
