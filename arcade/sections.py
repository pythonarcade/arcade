from typing import Optional, List

from arcade import Camera, draw_lrtb_rectangle_outline
from arcade.color import WHITE


class Section:
    """
    A Section represents a rectangular portion of the viewport
    Events are dispatched to the section based on it's position on the screen.
    """

    def __init__(self, view, left: float, bottom: float, width: float, height: float, *,
                 keyboard_primary: bool = False, prevent_dispatch: bool = True):
        # parent view
        self.view = view

        # section options
        self._keyboard_primary: bool = keyboard_primary
        self.prevent_dispatch: bool = prevent_dispatch

        # section position into the current viewport
        # if screen is resized it's upto the user to move or resize each section
        self.left: float = left
        self.bottom: float = bottom
        self.width: float = width
        self.height: float = height

        # optional section camera
        self.camera: Optional[Camera] = None

    @property
    def right(self) -> float:
        """ Right edge of this section """
        return self.left + self.width

    @property
    def top(self) -> float:
        """ Top edge of this section """
        return self.bottom + self.height

    @property
    def window(self):
        """ The view window """
        return self.view.window

    @property
    def keyboard_primary(self) -> bool:
        """ Sets if this section receives the keyboard events """
        return self._keyboard_primary

    @keyboard_primary.setter
    def keyboard_primary(self, value) -> None:
        if value is True:
            self.view.section_manager.remove_keyboard_primary()
            self._keyboard_primary = True
        else:
            self._keyboard_primary = value

    def overlaps_with(self, section) -> bool:
        """ Checks if this section overlaps with another section """
        return not (self.right < section.left or self.left > section.right or self.top < section.bottom or self.bottom > section.top)

    def mouse_is_on_top(self, x: float, y: float) -> bool:
        """ Check if the current mouse position is on top of this section """
        return self.left <= x <= self.right and self.bottom <= y <= self.top

    # Following methods are just the usual view methods + on_mouse_enter / on_mouse_leave

    def on_draw(self):
        pass

    def on_update(self, delta_time: float):
        pass

    def update(self, delta_time: float):
        pass

    def on_resize(self, width: int, height: int):
        pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        pass

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        pass

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, _buttons: int, _modifiers: int):
        pass

    def on_mouse_enter(self, x: float, y: float):
        pass

    def on_mouse_leave(self, x: float, y: float):
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, _symbol: int, _modifiers: int):
        pass


class SectionManager:
    """
    This manages the different Sections a View has.
    Actions such as dispatching the eventos to the correct Section, draw order, etc.
    """

    def __init__(self, view):
        self.view = view  # the view this section manager belongs to
        self.sections: List[Section] = []  # a list of the current sections for this view

        # generic camera to reset after a custom camera is use
        self.camera: Camera = Camera(self.view.window.width, self.view.window.height)

        # Holds the section the mouse is currently on top
        self.mouse_over_section: Optional[Section] = None

        # debug tool to just draw some rectangles over the section borders
        self.debug: bool = False

    @property
    def has_sections(self) -> bool:
        """ Returns true if sections are available """
        return bool(self.sections)

    def add_section(self, new_section: "Section") -> bool:
        """
        Ads a section to this Section Manger.
        It checks if the new section overlaps with other sections.
        """
        for section in self.sections:
            if new_section.overlaps_with(section):
                return False
        self.sections.append(new_section)
        return True

    def on_update(self, delta_time: float):
        """ Called on each event loop. First dispatch the view event, then the section ones. """
        self.view.on_update(delta_time)
        for section in self.sections:
            section.on_update(delta_time)

    def update(self, delta_time: float):
        """ Called on each event loop. First dispatch the view event, then the section ones. """
        self.view.update(delta_time)
        for section in self.sections:
            section.update(delta_time)

    def on_draw(self):
        """
        Called on each event loop. First dispatch the view event, then the section ones.
        It automatically calls camera.use() for each section that has a camera and resets
         the camera effects by calling the default SectionManager camera afterwards if needed.
        """
        self.view.on_draw()
        for section in self.sections:
            if section.camera:
                section.camera.use()  # call the camera use of the current section before section.on_draw
            section.on_draw()
            if section.camera:
                self.camera.use()  # reset to the default camera after the section is draw if needed
            if self.debug:
                draw_lrtb_rectangle_outline(section.left, section.right,
                                            section.top, section.bottom, WHITE)

    def on_resize(self, width: int, height: int):
        """ Called when the windows is resized. First dispatch the view event, then the section ones. """
        self.camera.resize(width, height)  # resize the default camera
        self.view.on_resize(width, height)
        for section in self.sections:
            section.on_resize(width, height)

    def get_keyboard_primary(self) -> Optional[Section]:
        """ Returns the section that has keyboard_primary set """
        for section in self.sections:
            if section.keyboard_primary:
                return section
        return None

    def remove_keyboard_primary(self) -> None:
        """ Removes the keyboard events handling from all sections """
        for section in self.sections:
            section._keyboard_primary = False

    def get_section(self, x: float, y: float) -> Optional[Section]:
        """ Returns a section based on a position """
        for section in self.sections:
            if section.mouse_is_on_top(x, y):
                return section
        return None

    def dispatch_mouse_event(self, event: str, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        """ Generic method to dispatch mouse events to the correct Section """
        # check if the affected section has been already computed
        section = kwargs.get('current_section')
        if section:
            # remove the section from the kwargs so it arrives clean to the event handler
            del kwargs['current_section']
        else:
            section = self.get_section(x, y)  # get the section from mouse position
        if section:
            method = getattr(section, event, None)  # get the method to call from the section
            if method:
                result = method(x, y, *args, **kwargs)  # call the section method
            if (method and result is True) or section.prevent_dispatch:
                # if the method returns EVENT_HANDLED (True) then avoid propagating the event.
                # if the section prevents dispatching events to the view return
                return True
        method = getattr(self.view, event, None)  # get the method from the view
        if method:
            return method(x, y, *args, **kwargs)  # call the view method

    def dispatch_keyboard_event(self, event, *args, **kwargs) -> Optional[bool]:
        """ Generic method to dispatch keyboard events to the correct Section """
        section = self.get_keyboard_primary()  # get the section that receives keyboard events if any
        if section:
            method = getattr(section, event, None)  # get the method to call from the section
            if method:
                result = method(*args, **kwargs)  # call the section method
            if (method and result is True) or section.prevent_dispatch:
                # if the method returns EVENT_HANDLED (True) then avoid propagating the event.
                # if the section prevents dispatching events to the view return
                return True
        method = getattr(self.view, event, None)  # get the method from the view
        if method:
            return method(*args, **kwargs)  # call the view method

    def on_mouse_press(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_mouse_event('on_mouse_press', x, y, *args, **kwargs)

    def on_mouse_release(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_mouse_event('on_mouse_release', x, y, *args, **kwargs)

    def on_mouse_motion(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        before_section = self.mouse_over_section
        current_section = self.get_section(x, y)
        if before_section is not current_section:
            self.mouse_over_section = current_section
            if before_section:
                # dispatch on_mouse_leave to before_section (result from this call is ignored)
                self.dispatch_mouse_event('on_mouse_leave', x, y, current_section=before_section)
            if current_section:
                # dispatch on_mouse_enter to current_section (result from this call is ignored)
                self.dispatch_mouse_event('on_mouse_enter', x, y, current_section=current_section)
        if current_section is not None:
            kwargs['current_section'] = current_section
        return self.dispatch_mouse_event('on_mouse_motion', x, y, *args, **kwargs)

    def on_mouse_scroll(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_mouse_event('on_mouse_scroll', x, y, *args, **kwargs)

    def on_mouse_drag(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_mouse_event('on_mouse_drag', x, y, *args, **kwargs)

    def on_mouse_enter(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        current_section = self.get_section(x, y)
        self.mouse_over_section = current_section  # set the section the mouse is over
        # pass the correct section to the dispatch event so it is not computed again
        kwargs['current_section'] = current_section
        return self.dispatch_mouse_event('on_mouse_enter', x, y, *args, **kwargs)

    def on_mouse_leave(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        if self.mouse_over_section:
            # clear the section the mouse is over as it's out of the screen
            kwargs['current_section'], self.mouse_over_section = self.mouse_over_section, None
            return self.dispatch_mouse_event('on_mouse_leave', x, y, *args, **kwargs)

    def on_key_press(self, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_keyboard_event('on_key_press', *args, **kwargs)

    def on_key_release(self, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_keyboard_event('on_key_release', *args, **kwargs)
