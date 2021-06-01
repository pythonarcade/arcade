"""

:py:class:`~arcade.gui.uielement` provide extended features which are useful while handling graphical user interaction.
while :py:class:`~arcade.gui.uielement` provides a base class which provides

- handling hover and focus state
- callback to render element
- basic :py:class:`~arcade.gui.uistyle` support
- element specific id for identification and styling

arcade gui comes with some common :py:class:`~arcade.gui.uielement`

:py:class:`arcade.gui.UILabel`
    simple text label

:py:class:`arcade.gui.UIInputbox`
    input field for text input, support for submit on enter

:py:class:`arcade.gui.UIImagebutton`
    button supporting images for normal, hover, press

:py:class:`arcade.gui.UIFlatbutton`
    flat style button

:py:class:`arcade.gui.UIGhostflatbutton`
    flat style button outlined

:py:class:`arcade.gui.UIToggle`
    toggle button with on/off state

To get an impression of these elements run ``python -m arcade.gui.examples.show_all``

"""
from abc import abstractmethod
from typing import Optional, Tuple, Set, TYPE_CHECKING
from uuid import uuid4

from pyglet.event import EventDispatcher

import arcade
from arcade import Texture
from arcade.gui.events import UIEvent, MOUSE_PRESS, MOUSE_RELEASE
from arcade.gui.exceptions import UIException
from arcade.gui.style import UIStyle

if TYPE_CHECKING:
    from arcade.gui.manager import UIManager


class UIElement(arcade.Sprite):
    """
    Base class for ui elements like :py:class:`arcade.gui.UILabel` or :py:class:`arcade.gui.UIImageButton`.

    :py:class:`arcade.gui.UIElement` provides :py:class:`arcade.gui.UIEvent` handling and callbacks for hover and focus.
    Furthermore it provides support for :py:class:`arcade.gui.UIStyle`, which makes customization of elements easier,
    and a id based identification.

    Style values are resolved depending on the
    :py:attr:`arcade.gui.UIElement().id`, :py:attr:`arcade.gui.UIElement().style_classes`,
    and element specific style attributes.

    :py:class:`arcade.gui.UIElement` implements :py:class:`arcade.Sprite`.
    Subclasses have to implement :py:meth:`arcade.gui.UIElement.render()` and set the :py:attr:`arcade.Sprite.texture`

    """

    def __init__(
        self,
        center_x=0,
        center_y=0,
        id: Optional[str] = None,
        style: UIStyle = None,
        min_size: Optional[Tuple] = None,
        size_hint: Optional[Tuple] = None,
        **kwargs,
    ):
        super().__init__()
        # ID for this element, to search in view by id or identify this element from an event
        self.__id = id
        self.mng: Optional["UIManager"] = None

        # unique id, to overwrite style for exactly this element, DONT CHANGE THIS LATER
        self.__style_id = str(uuid4())
        self.style_classes = ["globals"]
        self._style: UIStyle = style or UIStyle.default_style()
        self._style.push_handlers(self.on_style_change)

        # what do we need to look like a proper arcade.Sprite
        # self.texture <- subclass
        # self.width/height <- subclass
        self.center_x = center_x
        self.center_y = center_y

        self.min_size = min_size
        self.size_hint = size_hint

    def __repr__(self):
        return f"UIElement({self.id if self.id else self.__style_id})"

    @property
    def id(self) -> Optional[str]:
        """
        You can set id on creation, but it can't be modify later
        """
        return self.__id

    @id.setter
    def id(self, value):
        if len(self.sprite_lists) > 0:
            raise UIException("Setting id, after adding to a UIManager, is to late!")

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

        return value or default

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
        Callback for a :py:class:`arcade.gui.UIEvent`, triggered through :py:class:`pyglet.EventDispatcher`

        :param arcade.gui.UIEvent event: Dispatched event
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


class UIClickable(EventDispatcher, UIElement):
    """
    Texture based UIElement supporting hover and press,
    this should fit every use case.
    """

    CLICKED = "UIClickable_CLICKED"

    def __init__(
        self,
        center_x=0,
        center_y=0,
        id: Optional[str] = None,
        style: UIStyle = None,
        **kwargs,
    ):
        """
        Create a clickable UI Element

        :param center_x: Center X of element
        :param center_y: Center Y of element
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        super().__init__(center_x=center_x, center_y=center_y, id=id, style=style)
        self.register_event_type("on_click")

        self._pressed = False
        self._hovered = False
        self._focused = False

        self._normal_texture: Optional[Texture] = None
        self._hover_texture: Optional[Texture] = None
        self._press_texture: Optional[Texture] = None
        self._focus_texture: Optional[Texture] = None

    @property
    def normal_texture(self):
        return self._normal_texture

    @normal_texture.setter
    def normal_texture(self, texture: Texture):
        self._normal_texture = texture
        self.set_proper_texture()

    @property
    def hover_texture(self):
        return self._hover_texture

    @hover_texture.setter
    def hover_texture(self, texture: Texture):
        self._hover_texture = texture
        self.set_proper_texture()

    @property
    def press_texture(self):
        return self._press_texture

    @press_texture.setter
    def press_texture(self, texture: Texture):
        self._press_texture = texture
        self.set_proper_texture()

    @property
    def focus_texture(self):
        return self._focus_texture

    @focus_texture.setter
    def focus_texture(self, texture: Texture):
        self._focus_texture = texture
        self.set_proper_texture()

    @property
    def hovered(self):
        """
        True if mouse is over this element, only one element at a time
        """
        return self._hovered

    @hovered.setter
    def hovered(self, value):
        self._hovered = value
        self.set_proper_texture()

    @property
    def pressed(self):
        """
        True if mouse is over this element and mouse button gets pressed,
        only one element at a time
        """
        return self._pressed

    @pressed.setter
    def pressed(self, value):
        self._pressed = value
        self.set_proper_texture()

    @property
    def focused(self):
        """
        True if mouse is clicked on this element, until click outside of this element
        """
        return self._focused

    @focused.setter
    def focused(self, value):
        self._focused = value
        self.set_proper_texture()

    def on_ui_event(self, event: UIEvent):
        if event.type not in (MOUSE_PRESS, MOUSE_RELEASE):
            return

        left_click = event.get("button") == arcade.MOUSE_BUTTON_LEFT
        if not left_click:
            return

        if event.type == MOUSE_PRESS and self.collides_with_point(
            (event.get("x"), event.get("y"))
        ):
            self.on_press()
        elif event.type == MOUSE_RELEASE and self.pressed and self.focused:
            self.on_release()

            if self.collides_with_point((event.get("x"), event.get("y"))):
                self.dispatch_event("on_click")

                if self.mng:
                    self.mng.dispatch_ui_event(
                        UIEvent(UIClickable.CLICKED, ui_element=self)
                    )

    @abstractmethod
    def render(self):
        """
        Render and update textures, called on style change.
        Initially called while added to :py:class:`arcade.gui.UIManager`

        Has to be implemented by subclasses of :py:class:`arcade.gui.UIElement`.

        Recommendation: call :py:meth:`arcade.gui.UIClickable.set_proper_texture()`
        after setting up the textures if you don't use property textures which handle this.
        Property textures:
        * self.normal_texture
        * self.hover_texture
        * self.press_texture
        * self.focus_texture
        """
        raise NotImplementedError()

    def set_proper_texture(self):
        """ Set normal, mouse-over, or clicked texture. """
        if self.pressed and self.press_texture:
            self.texture = self.press_texture
        elif self.focused and self.focus_texture:
            self.texture = self.focus_texture
        elif self.hovered and self.hover_texture:
            self.texture = self.hover_texture
        else:
            self.texture = self.normal_texture

    def on_hover(self):
        self.hovered = True

    def on_unhover(self):
        self.hovered = False

    def on_focus(self):
        self.focused = True

    def on_unfocus(self):
        self.focused = False

    def on_press(self):
        self.pressed = True

    def on_release(self):
        self.pressed = False

    def on_click(self):
        """
        This callback will be triggered if
        * the Clickable is pressed
        * the Clickable is focused
        * MOUSE_RELEASE event triggered

        In case of multiple UIElements are overlapping, the last added to UIManager will be focused on MOUSE_RELEASE,
        so that only that one will trigger on_click.
        """
        pass
