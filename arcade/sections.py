from typing import Optional, List, Iterable

from arcade import Camera


class Section:
    """
    A Section represents a rectangular portion of the viewport
    Events are dispatched to the section based on it's position on the screen.
    """

    def __init__(self, left: float, bottom: float, width: float, height: float, *,
                 name: Optional[str] = None, accept_keyboard_events: bool = False,
                 prevent_dispatch: Optional[Iterable] = None, prevent_dispatch_view: Optional[Iterable] = None,
                 local_mouse_coordinates: bool = False, enabled: bool = True, modal: bool = False):

        # name of the section
        self.name: Optional[str] = name
        # parent view: set by the SectionManager
        self._view: Optional["View"] = None  # protected, you should not change section.view manually

        # section options
        self._enabled: bool = enabled  # enables or disables this section
        self._modal: bool = modal  # prevent the following sections from receiving input events and updating
        self.block_updates: bool = False  # if True update and on_update will not trigger in this section
        self.accept_keyboard_events: bool = accept_keyboard_events
        self.prevent_dispatch: Iterable = prevent_dispatch or {True}  # prevents events to propagate
        self.prevent_dispatch_view: Iterable = prevent_dispatch_view or {
            True}  # prevents events to propagate to the view
        self.local_mouse_coordinates: bool = local_mouse_coordinates  # mouse coordinates relative to section

        # section position into the current viewport
        # if screen is resized it's upto the user to move or resize each section
        self._left: float = left
        self._bottom: float = bottom
        self._width: float = width
        self._height: float = height
        self._right: float = left + width
        self._top: float = bottom + height

        # optional section camera
        self.camera: Optional[Camera] = None

    @property
    def view(self):
        """ The view this section is set on """
        return self._view

    @property
    def section_manager(self) -> Optional["SectionManager"]:
        """ Returns the section manager """
        return self._view.section_manager if self._view else None

    @property
    def enabled(self) -> bool:
        """ enables or disables this section """
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        if value is self._enabled:
            return
        self._enabled = value
        if value:
            self.on_show_section()
        else:
            self.on_hide_section()

    @property
    def modal(self) -> bool:
        """ returns the modal state (Prevent the following sections from receiving input events and updating) """
        return self._modal

    @property
    def left(self) -> float:
        """ Left edge of this section """
        return self._left

    @left.setter
    def left(self, value: float):
        self._left = value
        self._right = value + self._width

    @property
    def bottom(self) -> float:
        """ The bottom edge of this section """
        return self._bottom

    @bottom.setter
    def bottom(self, value: float):
        self._bottom = value
        self._top = value + self._height

    @property
    def width(self) -> float:
        """ The width of this section """
        return self._width

    @width.setter
    def width(self, value: float):
        self._width = value
        self._right = value + self._left

    @property
    def height(self) -> float:
        """ The height of this section """
        return self._height

    @height.setter
    def height(self, value: float):
        self._height = value
        self._top = value + self._bottom

    @property
    def right(self) -> float:
        """ Right edge of this section """
        return self._right

    @right.setter
    def right(self, value: float):
        self._right = value
        self._left = value - self._width

    @property
    def top(self) -> float:
        """ Top edge of this section """
        return self._top

    @top.setter
    def top(self, value: float):
        self._top = value
        self._bottom = value - self._height

    @property
    def ec_left(self) -> float:
        # Section event capture dimension. This attribute defines Left event capture area
        return 0.0 if self._modal else self._left

    @property
    def ec_right(self) -> float:
        # Section event capture dimension. This attribute defines Right event capture area
        return self.window.width if self._modal else self._right

    @property
    def ec_bottom(self) -> float:
        # Section event capture dimension. This attribute defines Bottom event capture area
        return 0.0 if self._modal else self._bottom

    @property
    def ec_top(self) -> float:
        # Section event capture dimension. This attribute defines Top event capture area
        return self.window.height if self._modal else self._top

    @property
    def window(self):
        """ The view window """
        return self.view.window

    def overlaps_with(self, section) -> bool:
        """ Checks if this section overlaps with another section """
        return not (self.right < section.left or self.left > section.right
                    or self.top < section.bottom or self.bottom > section.top)

    def mouse_is_on_top(self, x: float, y: float) -> bool:
        """ Check if the current mouse position is on top of this section """
        return self.ec_left <= x <= self.ec_right and self.ec_bottom <= y <= self.ec_top

    def get_xy_screen_relative(self, section_x: float, section_y: float):
        """ Returns screen coordinates from section coordinates """
        return self.left + section_x, self.bottom + section_y

    def get_xy_section_relative(self, screen_x: float, screen_y: float):
        """ returns section coordinates from screen coordinates """
        return screen_x - self.left, screen_y - self.bottom

    # Following methods are just the usual view methods
    #  + on_mouse_enter / on_mouse_leave / on_show_section / on_hide_section

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

    def on_show_section(self):
        pass

    def on_hide_section(self):
        pass


class SectionManager:
    """
    This manages the different Sections a View has.
    Actions such as dispatching the events to the correct Section, draw order, etc.
    """

    def __init__(self, view):
        self.view = view  # the view this section manager belongs to

        # store sections in update/event order and in draw order
        self._sections: List[Section] = []  # a list of the current sections for this in update/event order
        self._sections_draw: List[Section] = []  # the list of current sections in draw order

        # generic camera to reset after a custom camera is use
        # this camera is set to the whole viewport
        self.camera: Camera = Camera(self.view.window.width, self.view.window.height)

        # Holds the section the mouse is currently on top
        self.mouse_over_section: Optional[Section] = None

    @property
    def sections(self) -> List[Section]:
        return self._sections

    @property
    def has_sections(self) -> bool:
        """ Returns true if sections are available """
        return bool(self.sections)

    def disable(self) -> None:
        """ Disable all sections """
        for section in self.sections:
            section.enabled = False

    def enable(self) -> None:
        """ Enables all section """
        for section in self.sections:
            section.enabled = True

    def get_section_by_name(self, name: str) -> Optional[Section]:
        """ Returns the first section with the given name """
        sections = [section for section in self.sections if section.name == name]
        if sections:
            return sections[0]
        return None

    def add_section(self, section: "Section", at_index: Optional[int] = None) -> None:
        """
        Adds a section to this Section Manager
        :param section: the section to add to this section manager
        :param at_index: inserts the section at that index. If None at the end
        """
        if not isinstance(section, Section):
            raise ValueError('You can only add Section instances')
        section._view = self.view  # modify view param from section
        if at_index is None:
            self._sections.append(section)
        else:
            self._sections.insert(at_index, section)
        # keep sections order updated in the lists of sections to draw
        self._sections.sort(key=lambda s: 0 if s.modal else 1)  # modals go first
        self._sections_draw = sorted(self._sections, key=lambda s: 1 if s.modal else 0)  # modals go last

    def remove_section(self, section: "Section") -> None:
        """ Removes a section from this section manager """
        section._view = None
        self._sections.remove(section)

        # keep sections order updated in the lists of sections
        self._sections.sort(key=lambda s: 0 if s.modal else 1)  # modals go first
        self._sections_draw = sorted(self._sections, key=lambda s: 1 if s.modal else 0)  # modals go last

    def clear_sections(self):
        """ Removes all sections """
        for section in self.sections:
            section._view = None
        self._sections = []
        self._sections_draw = []

    def on_update(self, delta_time: float):
        """ Called on each event loop. First dispatch the view event, then the section ones. """
        modal_present = False
        self.view.on_update(delta_time)
        for section in self.sections:
            if section.enabled and not section.block_updates and not modal_present:
                section.on_update(delta_time)
                if section.modal:
                    modal_present = True

    def update(self, delta_time: float):
        """ Called on each event loop. First dispatch the view event, then the section ones. """
        modal_present = False
        self.view.update(delta_time)
        for section in self.sections:
            if section.enabled and not section.block_updates and not modal_present:
                section.update(delta_time)
                if section.modal:
                    modal_present = True

    def on_draw(self):
        """
        Called on each event loop. First dispatch the view event, then the section ones.
        It automatically calls camera.use() for each section that has a camera and resets
        the camera effects by calling the default SectionManager camera afterwards if needed.
        """
        self.view.on_draw()
        for section in self._sections_draw:  # iterate over sections_draw
            if not section.enabled:
                continue
            if section.camera:
                section.camera.use()  # call the camera use of the current section before section.on_draw
            section.on_draw()
            if section.camera:
                self.camera.use()  # reset to the default camera after the section is draw if needed

    def on_resize(self, width: int, height: int):
        """ Called when the window is resized. First dispatch the view event, then the section ones. """
        self.camera.resize(width, height)  # resize the default camera
        self.view.on_resize(width, height)  # call resize on the view
        for section in self.sections:
            if section.enabled:
                section.on_resize(width, height)

    def disable_all_keyboard_events(self) -> None:
        """ Removes the keyboard events handling from all sections """
        for section in self.sections:
            section.accept_keyboard_events = False

    def get_section(self, x: float, y: float) -> Optional[Section]:
        """ Returns the first section based on x,y position """
        for section in self.sections:
            if section.enabled and section.mouse_is_on_top(x, y):
                return section
        return None

    def dispatch_mouse_event(self, event: str, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        """ Generic method to dispatch mouse events to the correct Section """
        # check if the affected section has been already computed
        prevent_dispatch = False
        section = kwargs.get('current_section')
        if section:
            # remove the section from the kwargs, so it arrives clean to the event handler
            del kwargs['current_section']
        else:
            section = self.get_section(x, y)  # get the section from mouse position
        if section:
            method = getattr(section, event, None)  # get the method to call from the section
            if method:
                if section.local_mouse_coordinates:
                    position = section.get_xy_section_relative(x, y)
                else:
                    position = x, y
                prevent_dispatch = method(*position, *args, **kwargs)  # call the section method
                prevent_dispatch = True if section.modal else prevent_dispatch  # prevent dispatch if modal
                if prevent_dispatch is True or any(test in section.prevent_dispatch for test in [True, event]):
                    # prevent_dispatch attributte from section only affects if
                    #  the method is implemented in the same section
                    prevent_dispatch = True
        if section and any(test in section.prevent_dispatch_view for test in [True, event]):
            # if the section prevents dispatching events to the view return
            return prevent_dispatch

        # call the method from the view.
        view_prevent_dispatch = False
        method = getattr(self.view, event, None)  # get the method from the view
        if method:
            view_prevent_dispatch = method(x, y, *args, **kwargs)  # call the view method
        return view_prevent_dispatch or prevent_dispatch

    def dispatch_keyboard_event(self, event, *args, **kwargs) -> Optional[bool]:
        """ Generic method to dispatch keyboard events to the correct sections """
        # get the sections that receive keyboard events if any
        propagate_to_view = True
        prevent_dispatch = False
        for section in self.sections:
            if prevent_dispatch:
                break
            if not section.enabled:
                continue
            if section.accept_keyboard_events:
                if any(test in section.prevent_dispatch_view for test in [True, event]):
                    propagate_to_view = False
                method = getattr(section, event, None)  # get the method to call from the section
                if method:
                    prevent_dispatch = method(*args, **kwargs)  # call the section method
                    if prevent_dispatch is True or any(test in section.prevent_dispatch for test in [True, event]):
                        # prevent_dispatch attributte from section only affects if
                        #  the method is implemented in the same section
                        prevent_dispatch = True
            if section.modal:
                # if this section is modal, then avoid passing any event to more sections
                return prevent_dispatch

        if propagate_to_view is False:
            return prevent_dispatch

        method = getattr(self.view, event, None)  # get the method from the view
        if method:
            return method(*args, **kwargs) or prevent_dispatch  # call the view method

        return False

    def on_mouse_press(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_mouse_event('on_mouse_press', x, y, *args, **kwargs)

    def on_mouse_release(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_mouse_event('on_mouse_release', x, y, *args, **kwargs)

    def on_mouse_motion(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        """
        This method dispatches the on_mouse_motion and also calculates
         if on_mouse_enter/leave should be fired
        """
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
        # pass the correct section to the dispatch event, so it is not computed again
        kwargs['current_section'] = current_section
        return self.dispatch_mouse_event('on_mouse_enter', x, y, *args, **kwargs)

    def on_mouse_leave(self, x: float, y: float, *args, **kwargs) -> Optional[bool]:
        if self.mouse_over_section:
            # clear the section the mouse is over as it's out of the screen
            kwargs['current_section'], self.mouse_over_section = self.mouse_over_section, None
            return self.dispatch_mouse_event('on_mouse_leave', x, y, *args, **kwargs)

        return False

    def on_key_press(self, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_keyboard_event('on_key_press', *args, **kwargs)

    def on_key_release(self, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_keyboard_event('on_key_release', *args, **kwargs)

    def on_show_view(self):
        for section in self.sections:
            if section.enabled:
                section.on_show_section()

    def on_hide_view(self):
        for section in self.sections:
            if section.enabled:
                section.on_hide_section()
