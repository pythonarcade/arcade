from typing import Optional

from pyglet.event import EventDispatcher

from arcade import Texture

from arcade.gui import UIElement, UIEvent, MOUSE_PRESS, MOUSE_RELEASE
from arcade.gui.ui_style import UIStyle


class UIClickable(EventDispatcher, UIElement):
    """ Texture based UIElement supporting hover and press, this should fit every use case"""

    CLICKED = 'UIClickable_CLICKED'

    def __init__(self,
                 center_x=0, center_y=0,
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            id=id,
            style=style
        )
        self.register_event_type('on_click')

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
        return self._hovered

    @hovered.setter
    def hovered(self, value):
        self._hovered = value
        self.set_proper_texture()

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, value):
        self._pressed = value
        self.set_proper_texture()

    @property
    def focused(self):
        return self._focused

    @focused.setter
    def focused(self, value):
        self._focused = value
        self.set_proper_texture()

    def on_ui_event(self, event: UIEvent):
        if event.type == MOUSE_PRESS and self.collides_with_point((event.get('x'), event.get('y'))):
            self.on_press()
        elif event.type == MOUSE_RELEASE and self.pressed:
            if self.pressed:
                self.on_release()

                if self.collides_with_point((event.get('x'), event.get('y'))):
                    self.dispatch_event('on_click')

                    if self.mng:
                        self.mng.disptach_ui_event(UIEvent(UIClickable.CLICKED, ui_element=self))

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
        pass
