import typing
from typing import Optional
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
    def __init__(self, type: str, **kwargs):
        self.type = type
        self.__dict__.update(**kwargs)

        self._repr_keys = tuple(kwargs.keys())

    def __str__(self):
        return ' '.join([f'{self.type} ', *[f'{key}={getattr(self, key)}' for key in self._repr_keys]])


class UIElement(arcade.Sprite):
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
        self._style = style if style else UIStyle.default_style()

        # what do we need to look like a proper arcade.Sprite
        # self.texture <- subclass
        # self.width/height <- subclass
        self.center_x = center_x
        self.center_y = center_y

    @property
    def id(self) -> str:
        """
        You can set id on creation, but not modify later
        """
        return self.__id

    @id.setter
    def id(self, value):
        if len(self.sprite_lists) > 0:
            raise UIException('Setting id after adding to a view is to late!')

        self.__id = value

    @property
    def style(self):
        return self._style

    def set_style_attrs(self, **kwargs):
        """
        Sets a custom style attribute for this UIElement
        The value will be returned unparsed (like given)
        Setting an attribute to None will remove the overwrite, defaults will apply

        :param kwargs: key-value pairs
        """
        style_data = self._style.get_class(self.__style_id)

        for key, value in kwargs.items():
            if value is None:
                if key in style_data:
                    del style_data[key]
            else:
                style_data[key] = value

        self.render()

    def style_attr(self, key, default=None):
        lookup_classes = [*self.style_classes, self.id, self.__style_id]
        value = self._style.get_attr(lookup_classes, key)

        return value if value else default

    def render(self):
        """
        Optinally render own textures, a style change may be indicated
        # TODO looks like a not to bad pattern to have a render function, which renders textures and can be used to
        # TODO refresh those in case of some style change!
        """
        pass

    def on_ui_event(self, event: UIEvent):
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
    pass
