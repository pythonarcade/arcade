from typing import TYPE_CHECKING, Optional, List, Iterable, Union, Set

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED

from arcade import SimpleCamera, get_window

if TYPE_CHECKING:
    from arcade import View


class Section:
    """
    A Section represents a rectangular portion of the viewport
    Events are dispatched to the section based on it's position on the screen.
    """

    def __init__(self, left: int, bottom: int, width: int, height: int,
                 *, name: Optional[str] = None,
                 accept_keyboard_keys: Union[bool, Iterable] = True,
                 accept_mouse_events: Union[bool, Iterable] = True,
                 prevent_dispatch: Optional[Iterable] = None,
                 prevent_dispatch_view: Optional[Iterable] = None,
                 local_mouse_coordinates: bool = False,
                 enabled: bool = True, modal: bool = False):
        """
        :param int left: the left position of this section
        :param int bottom: the bottom position of this section
        :param int width: the width of this section
        :param int height: the height of this section
        :param Optional[str] name: the name of this section
        :param Union[bool, Iterable] accept_keyboard_keys: whether or not this section captures keyboard keys through.
            keyboard events. If the param is an iterable means the keyboard keys that are captured in press/release
            events: for example: [arcade.key.UP, arcade.key.DOWN] will only capture this two keys
        :param Union[bool, Iterable] accept_mouse_events: whether or not this section captures mouse events.
            If the param is an iterable means the mouse events that are captured.
            for example: ['on_mouse_press', 'on_mouse_release'] will only capture this two events.
        :param Optional[Iterable] prevent_dispatch: a list of event names that will not be dispatched to subsequent
            sections. You can pass None (default) or {True} to prevent the dispatch of all events.
        :param Optional[Iterable] prevent_dispatch_view: a list of event names that will not be dispatched to the view.
            You can pass None (default) or {True} to prevent the dispatch of all events to the view.
        :param bool local_mouse_coordinates: if True the section mouse events will receive x, y coordinates section
            related to the section dimensions and position (not related to the screen)
        :param bool enabled: if False the section will not capture any events
        """
        # name of the section
        self.name: Optional[str] = name

        # parent view: set by the SectionManager. Protected, you should not change section.view manually
        self._view: Optional["View"] = None

        # section options
        self._enabled: bool = enabled  # enables or disables this section
        # prevent the following sections from receiving input events and updating
        self._modal: bool = modal
        # if True 'update' and 'on_update' will not trigger in this section
        self.block_updates: bool = False

        # arcade keyboard keys to accept.
        self.accept_keyboard_keys: Union[bool, Iterable] = accept_keyboard_keys
        # arcade moouse events to accept.
        self.accept_mouse_events: Union[bool, Iterable] = accept_mouse_events

        # prevents events to propagate
        self.prevent_dispatch: Iterable = prevent_dispatch or {True}
        # prevents events to propagate to the view
        self.prevent_dispatch_view: Iterable = prevent_dispatch_view or {True}
        # mouse coordinates relative to section
        self.local_mouse_coordinates: bool = local_mouse_coordinates

        # section position into the current viewport
        # if screen is resized it's upto the user to move or resize each section (section will receive on_resize event)
        self._left: int = left
        self._bottom: int = bottom
        self._width: int = width
        self._height: int = height
        self._right: int = left + width
        self._top: int = bottom + height

        # optional section camera
        self.camera: Optional[SimpleCamera] = None

    def __repr__(self):
        name = f'Section {self.name}' if self.name else 'Section'
        dimensions = (self.left, self.right, self.top, self.bottom)
        return f'{name} at {dimensions} '

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
        """
        Returns the modal state (Prevent the following sections from
        receiving input events and updating)
        """
        return self._modal

    @property
    def left(self) -> int:
        """ Left edge of this section """
        return self._left

    @left.setter
    def left(self, value: int):
        self._left = value
        self._right = value + self._width

    @property
    def bottom(self) -> int:
        """ The bottom edge of this section """
        return self._bottom

    @bottom.setter
    def bottom(self, value: int):
        self._bottom = value
        self._top = value + self._height

    @property
    def width(self) -> int:
        """ The width of this section """
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value
        self._right = value + self._left

    @property
    def height(self) -> int:
        """ The height of this section """
        return self._height

    @height.setter
    def height(self, value: int):
        self._height = value
        self._top = value + self._bottom

    @property
    def right(self) -> int:
        """ Right edge of this section """
        return self._right

    @right.setter
    def right(self, value: int):
        self._right = value
        self._left = value - self._width

    @property
    def top(self) -> int:
        """ Top edge of this section """
        return self._top

    @top.setter
    def top(self, value: int):
        self._top = value
        self._bottom = value - self._height

    @property
    def ec_left(self) -> int:
        # Section event capture dimension.
        # This attribute defines Left event capture area
        return 0 if self._modal else self._left

    @property
    def ec_right(self) -> int:
        # Section event capture dimension.
        # This attribute defines Right event capture area
        return self.window.width if self._modal else self._right

    @property
    def ec_bottom(self) -> int:
        # Section event capture dimension.
        # This attribute defines Bottom event capture area
        return 0 if self._modal else self._bottom

    @property
    def ec_top(self) -> int:
        # Section event capture dimension.
        # This attribute defines Top event capture area
        return self.window.height if self._modal else self._top

    @property
    def window(self):
        """ The view window """
        if getattr(self, '_view', None) is None or self._view is None:
            return get_window()
        else:
            return self._view.window

    def overlaps_with(self, section: "Section") -> bool:
        """ Checks if this section overlaps with another section """
        return not (self.right < section.left or self.left > section.right
                    or self.top < section.bottom or self.bottom > section.top)

    def mouse_is_on_top(self, x: int, y: int) -> bool:
        """ Check if the current mouse position is on top of this section """
        test_x = self.ec_left <= x <= self.ec_right
        test_y = self.ec_bottom <= y <= self.ec_top
        return test_x and test_y

    def get_xy_screen_relative(self, section_x: int, section_y: int):
        """ Returns screen coordinates from section coordinates """
        return self.left + section_x, self.bottom + section_y

    def get_xy_section_relative(self, screen_x: int, screen_y: int):
        """ returns section coordinates from screen coordinates """
        return screen_x - self.left, screen_y - self.bottom

    # Following methods are just the usual view methods
    #  + on_mouse_enter / on_mouse_leave / on_show_section / on_hide_section

    def on_draw(self):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_resize(self, width: int, height: int):
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        pass

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        pass

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        pass

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int,
                      _buttons: int, _modifiers: int):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_enter(self, x: int, y: int):
        pass

    def on_mouse_leave(self, x: int, y: int):
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

    def __init__(self, view: "View"):
        self.view: "View" = view  # the view this section manager belongs to

        # store sections in update/event order and in draw order
        # a list of the current sections for this in update/event order
        self._sections: List[Section] = []

        # the list of current sections in draw order
        self._sections_draw: List[Section] = []

        # generic camera to reset after a custom camera is use
        # this camera is set to the whole viewport
        self.camera: SimpleCamera = SimpleCamera(viewport=(0, 0,
                                                           self.view.window.width,
                                                           self.view.window.height))

        # Holds the section the mouse is currently on top
        self.mouse_over_section: Optional[Section] = None

        # True will call view.on_draw before sections on_draw, False after, None will not call view on_draw
        self.view_draw_first: Optional[bool] = True
        # True will call view.on_update before sections on_update, False after, None will not call view on_update
        self.view_update_first: Optional[bool] = True
        # True will call view.on_resize before sections on_resize, False after, None will not call view on_resize
        self.view_resize_first: Optional[bool] = True

        # Events that the section manager should handle (instead of the View) if sections are present in a View
        self.managed_events: Set = {
            'on_mouse_motion', 'on_mouse_drag', 'on_mouse_press',
            'on_mouse_release', 'on_mouse_scroll', 'on_mouse_enter',
            'on_mouse_leave', 'on_key_press', 'on_key_release', 'on_draw',
            'on_update', 'on_resize'}

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
        # modals go first
        self._sections.sort(key=lambda s: 0 if s.modal else 1)
        # modals go last
        self._sections_draw = sorted(self._sections, key=lambda s: 1 if s.modal else 0)

    def remove_section(self, section: Section) -> None:
        """ Removes a section from this section manager """
        section._view = None
        self._sections.remove(section)

        # keep sections order updated in the lists of sections
        # modals go first
        self._sections.sort(key=lambda s: 0 if s.modal else 1)
        # modals go last
        self._sections_draw = sorted(self._sections, key=lambda s: 1 if s.modal else 0)

    def clear_sections(self) -> None:
        """ Removes all sections """
        for section in self.sections:
            section._view = None
        self._sections = []
        self._sections_draw = []

    def on_update(self, delta_time: float) -> None:
        """
        Called on each event loop. First dispatch the view event, then the section ones.
        """
        modal_present = False
        if self.view_update_first is True:
            self.view.on_update(delta_time)
        for section in self.sections:
            if section.enabled and not section.block_updates and not modal_present:
                section.on_update(delta_time)
                if section.modal:
                    modal_present = True
        if self.view_update_first is False:
            self.view.on_update(delta_time)

    def on_draw(self) -> None:
        """
        Called on each event loop.
        First dispatch the view event, then the section ones.
        It automatically calls camera.use() for each section that has a camera and resets the camera
         effects by calling the default SectionManager camera afterwards if needed.
        """
        if self.view_draw_first is True:
            self.view.on_draw()
        for section in self._sections_draw:  # iterate over sections_draw
            if not section.enabled:
                continue
            if section.camera:
                # use the camera of the current section before section.on_draw
                section.camera.use()
            section.on_draw()
            if section.camera:
                # reset to the default camera after the section is drawn
                self.camera.use()
        if self.view_draw_first is False:
            self.view.on_draw()

    def on_resize(self, width: int, height: int) -> None:
        """
        Called when the window is resized.
        First dispatch the view event, then the section ones.
        """
        self.camera.resize(width, height)  # resize the default camera
        if self.view_resize_first is True:
            self.view.on_resize(width, height)  # call resize on the view
        for section in self.sections:
            if section.enabled:
                section.on_resize(width, height)
        if self.view_resize_first is False:
            self.view.on_resize(width, height)  # call resize on the view

    def disable_all_keyboard_events(self) -> None:
        """ Removes the keyboard events handling from all sections """
        for section in self.sections:
            section.accept_keyboard_keys = False

    def get_section(self, x: int, y: int) -> Optional[Section]:
        """ Returns the first section based on x,y position """
        for section in self.sections:
            if section.enabled and section.mouse_is_on_top(x, y):
                return section
        return None

    def dispatch_mouse_event(self, event: str, x: int, y: int, *args, **kwargs) -> Optional[bool]:
        """ Generic method to dispatch mouse events to the correct Section """
        # check if the affected section has been already computed
        prevent_dispatch = EVENT_UNHANDLED

        section_pre_computed = 'current_section' in kwargs
        if section_pre_computed:
            section = kwargs['current_section']
            # remove the section from the kwargs,
            # so it arrives clean to the event handler
            del kwargs['current_section']
        else:
            # get the section from mouse position
            section = self.get_section(x, y)
        if section:
            mouse_events_allowed = section.accept_mouse_events
            if mouse_events_allowed is False:
                prevent_dispatch = EVENT_UNHANDLED
            if mouse_events_allowed is True or event in mouse_events_allowed:  # event allowed
                # get the method to call from the section
                method = getattr(section, event, None)
                if method:
                    if section.local_mouse_coordinates:
                        position = section.get_xy_section_relative(x, y)
                    else:
                        position = x, y

                    # call the section method
                    prevent_dispatch = method(*position, *args, **kwargs)
                    # prevent dispatch if modal
                    prevent_dispatch = EVENT_HANDLED if section.modal else prevent_dispatch
                    if prevent_dispatch is EVENT_HANDLED or any(
                            test in section.prevent_dispatch for test in [True, event]):
                        # prevent_dispatch attributte from section only affects if
                        #  the method is implemented in the same section
                        prevent_dispatch = EVENT_HANDLED
        if section and any(test in section.prevent_dispatch_view for test in [True, event]):
            # if the section prevents dispatching events to the view return
            return prevent_dispatch

        # call the method from the view.
        view_prevent_dispatch = EVENT_UNHANDLED
        method = getattr(self.view, event, None)  # get the method from the view
        if method:
            # call the view method
            view_prevent_dispatch = method(x, y, *args, **kwargs)
        return view_prevent_dispatch or prevent_dispatch

    def dispatch_keyboard_event(self, event, *args, **kwargs) -> Optional[bool]:
        """
        Generic method to dispatch keyboard events to the correct sections
        """
        propagate_to_view = True
        prevent_dispatch = EVENT_UNHANDLED
        for section in self.sections:
            if prevent_dispatch:
                break
            if not section.enabled:
                continue
            keys_allowed = section.accept_keyboard_keys
            if keys_allowed is False:
                continue
            if keys_allowed is True or args[0] in keys_allowed or args in keys_allowed:
                if any(test in section.prevent_dispatch_view for test in [True, event]):
                    propagate_to_view = False
                # get the method to call from the section
                method = getattr(section, event, None)
                if method:
                    # call the section method
                    prevent_dispatch = method(*args, **kwargs)
                    if prevent_dispatch is EVENT_HANDLED or any(
                            test in section.prevent_dispatch for test in [True, event]):
                        # prevent_dispatch attributte from section only affect
                        #  if the method is implemented in the same section
                        prevent_dispatch = EVENT_HANDLED
            if section.modal:
                # if this section is modal, then avoid passing any event
                # to more sections
                return prevent_dispatch

        if propagate_to_view is False:
            return prevent_dispatch

        method = getattr(self.view, event, None)  # get the method from the view
        if method:
            # call the view method
            return method(*args, **kwargs) or prevent_dispatch
        return EVENT_UNHANDLED

    def on_mouse_press(self, x: int, y: int, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_mouse_event('on_mouse_press', x, y, *args,
                                         **kwargs)

    def on_mouse_release(self, x: int, y: int, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_mouse_event('on_mouse_release', x, y, *args,
                                         **kwargs)

    def on_mouse_motion(self, x: int, y: int, *args, **kwargs) -> Optional[bool]:
        """
        This method dispatches the on_mouse_motion and also calculates
         if on_mouse_enter/leave should be fired
        """
        before_section = self.mouse_over_section
        current_section = self.get_section(x, y)
        if before_section is not current_section:
            self.mouse_over_section = current_section
            if before_section:
                # dispatch on_mouse_leave to before_section
                # (result from this call is ignored)
                self.dispatch_mouse_event('on_mouse_leave', x, y, current_section=before_section)
            if current_section:
                # dispatch on_mouse_enter to current_section
                # (result from this call is ignored)
                self.dispatch_mouse_event('on_mouse_enter', x, y, current_section=current_section)
        if current_section is not None:
            kwargs['current_section'] = current_section
        return self.dispatch_mouse_event('on_mouse_motion', x, y, *args, **kwargs)

    def on_mouse_scroll(self, x: int, y: int, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_mouse_event('on_mouse_scroll', x, y, *args, **kwargs)

    def on_mouse_drag(self, x: int, y: int, *args, **kwargs) -> Optional[bool]:
        """
        This method dispatches the on_mouse_drag and also calculates
         if on_mouse_enter/leave should be fired
        """
        before_section = self.mouse_over_section
        current_section = self.get_section(x, y)
        if before_section is not current_section:
            self.mouse_over_section = current_section
            if before_section:
                # dispatch on_mouse_leave to before_section
                # (result from this call is ignored)
                self.dispatch_mouse_event('on_mouse_leave', x, y, current_section=before_section)
            if current_section:
                # dispatch on_mouse_enter to current_section
                # (result from this call is ignored)
                self.dispatch_mouse_event('on_mouse_enter', x, y, current_section=current_section)
        if current_section is not None:
            kwargs['current_section'] = current_section
        return self.dispatch_mouse_event('on_mouse_drag', x, y, *args, **kwargs)

    def on_mouse_enter(self, x: int, y: int, *args, **kwargs) -> Optional[bool]:
        current_section = self.get_section(x, y)
        # set the section the mouse is over
        self.mouse_over_section = current_section
        # pass the correct section to the dispatch event,
        # so it is not computed again
        kwargs['current_section'] = current_section
        return self.dispatch_mouse_event('on_mouse_enter', x, y, *args, **kwargs)

    def on_mouse_leave(self, x: int, y: int, *args, **kwargs) -> Optional[bool]:
        if self.mouse_over_section:
            # clear the section the mouse is over as it's out of the screen
            kwargs['current_section'], self.mouse_over_section = self.mouse_over_section, None
            return self.dispatch_mouse_event('on_mouse_leave', x, y, *args, **kwargs)
        return False

    def on_key_press(self, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_keyboard_event('on_key_press', *args, **kwargs)

    def on_key_release(self, *args, **kwargs) -> Optional[bool]:
        return self.dispatch_keyboard_event('on_key_release', *args, **kwargs)

    def on_show_view(self) -> None:
        """ Called when the view is shown """
        for section in self.sections:
            if section.enabled:
                section.on_show_section()

    def on_hide_view(self) -> None:
        """ Called when the view is hide """
        for section in self.sections:
            if section.enabled:
                section.on_hide_section()
