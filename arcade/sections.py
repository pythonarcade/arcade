from __future__ import annotations

import math
from typing import TYPE_CHECKING, Generator, Iterable

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED

from arcade import get_window
from arcade.camera.default import DefaultProjector
from arcade.types.rect import LRBT, Rect

if TYPE_CHECKING:
    from arcade import View
    from arcade.camera import Projector

__all__ = ["Section", "SectionManager"]


class Section:
    """
    A Section represents a rectangular portion of the viewport
    Events are dispatched to the section based on it's position on the screen.

    :param left: the left position of this section
    :param bottom: the bottom position of this section
    :param width: the width of this section
    :param height: the height of this section
    :param name: the name of this section
    :param bool | Iterable accept_keyboard_keys: whether or not this section
        captures keyboard keys through. keyboard events. If the param is an iterable
        means the keyboard keys that are captured in press/release events:
        for example: ``[arcade.key.UP, arcade.key.DOWN]`` will only capture this two keys
    :param bool  Iterable accept_mouse_events: whether or not this section
        captures mouse events. If the param is an iterable means the mouse events
        that are captured. for example: ``['on_mouse_press', 'on_mouse_release']``
        will only capture this two events.
    :param prevent_dispatch: a list of event names that will not be dispatched to subsequent
        sections. You can pass None (default) or {True} to prevent the dispatch of all events.
    :param prevent_dispatch_view: a list of event names that will not be dispatched to the view.
        You can pass None (default) or {True} to prevent the dispatch of all events to the view.
    :param local_mouse_coordinates: if True the section mouse events will receive x, y
        coordinates section related to the section dimensions and position (not related
        to the screen)
    :param enabled: if False the section will not capture any events
    :param modal: if True the section will be a modal section: will prevent updates
        and event captures on other sections. Will also draw last (on top) but capture
        events first.
    :param draw_order: The order this section will have when on_draw is called.
        The lower the number the earlier this will get draw.
        This can be different from the event capture order or the on_update order which
        is defined by the insertion order.
    """

    def __init__(
        self,
        left: int,
        bottom: int,
        width: int,
        height: int,
        *,
        name: str | None = None,
        accept_keyboard_keys: bool | Iterable = True,
        accept_mouse_events: bool | Iterable = True,
        prevent_dispatch: Iterable | None = None,
        prevent_dispatch_view: Iterable | None = None,
        local_mouse_coordinates: bool = False,
        enabled: bool = True,
        modal: bool = False,
        draw_order: int = 1,
    ):
        # name of the section
        self.name: str | None = name

        # parent view: set by the SectionManager. Protected, you should not change
        # section.view manually
        self._view: View | None = None

        # section options
        self._enabled: bool = enabled  # enables or disables this section
        # prevent the following sections from receiving input events and updating
        self._modal: bool = modal

        # set draw_order: the lower the number the earlier this section will get draw
        self._draw_order: int = draw_order

        # if True 'update' and 'on_update' will not trigger in this section
        self.block_updates: bool = False

        # arcade keyboard keys to accept.
        self.accept_keyboard_keys: bool | Iterable = accept_keyboard_keys
        # arcade mouse events to accept.
        self.accept_mouse_events: bool | Iterable = accept_mouse_events

        # prevents events to propagate
        self.prevent_dispatch: Iterable = prevent_dispatch or {True}
        # prevents events to propagate to the view
        self.prevent_dispatch_view: Iterable = prevent_dispatch_view or {True}
        # mouse coordinates relative to section
        self.local_mouse_coordinates: bool = local_mouse_coordinates

        # section position into the current viewport
        # if screen is resized it's upto the user to move or resize each section
        # (section will receive on_resize event)
        self._left: int = left
        self._bottom: int = bottom
        self._width: int = width
        self._height: int = height
        self._right: int = left + width
        self._top: int = bottom + height

        # section event capture dimensions
        # if section is modal, capture all events on the screen
        self._ec_left: int = 0 if self._modal else self._left
        self._ec_right: int = self.window.width if self._modal else self._right
        self._ec_bottom: int = 0 if self._modal else self._bottom
        self._ec_top: int = self.window.height if self._modal else self._top

        # optional section camera
        self.camera: Projector | None = None

    def __repr__(self):
        name = f"Section {self.name}" if self.name else "Section"
        dimensions = (self.left, self.right, self.top, self.bottom)
        return f"{name} at {dimensions} "

    @property
    def view(self):
        """The view this section is set on"""
        return self._view

    @property
    def section_manager(self) -> SectionManager | None:
        """Returns the section manager"""
        return self._view.section_manager if self._view else None

    @property
    def enabled(self) -> bool:
        """Enables or disables this section"""
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
    def draw_order(self) -> int:
        """
        Returns the draw order state
        The lower the number the earlier this section will get draw
        """
        return self._draw_order

    @draw_order.setter
    def draw_order(self, value: int) -> None:
        """
        Sets this section draw order
        The lower the number the earlier this section will get draw
        """
        self._draw_order = value
        if self.section_manager is not None:
            self.section_manager.sort_sections_draw_order()

    @property
    def left(self) -> int:
        """Left edge of this section"""
        return self._left

    @left.setter
    def left(self, value: int):
        self._left = value
        self._right = value + self._width
        self._ec_left = 0 if self._modal else value
        self._ec_right = self.window.width if self._modal else self._right

    @property
    def bottom(self) -> int:
        """The bottom edge of this section"""
        return self._bottom

    @bottom.setter
    def bottom(self, value: int):
        self._bottom = value
        self._top = value + self._height
        self._ec_bottom = 0 if self._modal else value
        self._ec_top = self.window.height if self._modal else self._top

    @property
    def width(self) -> int:
        """The width of this section"""
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value
        self._right = value + self._left
        self._ec_right = self.window.width if self._modal else self._right

    @property
    def height(self) -> int:
        """The height of this section"""
        return self._height

    @height.setter
    def height(self, value: int):
        self._height = value
        self._top = value + self._bottom
        self._ec_top = self.window.height if self._modal else self._top

    @property
    def right(self) -> int:
        """Right edge of this section"""
        return self._right

    @right.setter
    def right(self, value: int):
        self._right = value
        self._left = value - self._width
        self._ec_right = self.window.width if self._modal else value
        self._ec_left = 0 if self._modal else self._left

    @property
    def top(self) -> int:
        """Top edge of this section"""
        return self._top

    @top.setter
    def top(self, value: int):
        self._top = value
        self._bottom = value - self._height
        self._ec_top = self.window.height if self._modal else value
        self._ec_bottom = 0 if self._modal else self._bottom

    @property
    def rect(self) -> Rect:
        return LRBT(self.left, self.right, self.bottom, self.top)

    @property
    def window(self):
        """The view window"""
        if getattr(self, "_view", None) is None or self._view is None:
            return get_window()
        else:
            return self._view.window

    def overlaps_with(self, section: "Section") -> bool:
        """Checks if this section overlaps with another section"""
        return not (
            self.right < section.left
            or self.left > section.right
            or self.top < section.bottom
            or self.bottom > section.top
        )

    def mouse_is_on_top(self, x: int, y: int) -> bool:
        """Check if the current mouse position is on top of this section"""
        test_x = self._left <= x <= self._right
        test_y = self._bottom <= y <= self._top
        return test_x and test_y

    def should_receive_mouse_event(self, x: int, y: int) -> bool:
        """Check if the current section should receive a mouse event at a given position"""
        test_x = self._ec_left <= x <= self._ec_right
        test_y = self._ec_bottom <= y <= self._ec_top
        return test_x and test_y

    def get_xy_screen_relative(self, section_x: int, section_y: int):
        """Returns screen coordinates from section coordinates"""
        return self.left + section_x, self.bottom + section_y

    def get_xy_section_relative(self, screen_x: int, screen_y: int):
        """returns section coordinates from screen coordinates"""
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

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int):
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
        self._sections: list[Section] = []

        # the list of current sections in draw order
        self._sections_draw: list[Section] = []

        # generic camera to reset after a custom camera is use
        # this camera is set to the whole viewport
        self.camera: DefaultProjector = DefaultProjector()

        # Holds the section the mouse is currently on top
        self.mouse_over_sections: list[Section] = []

        # True will call view.on_draw before sections on_draw, False after,
        # None will not call view on_draw
        self.view_draw_first: bool | None = True
        # True will call view.on_update before sections on_update, False after,
        # None will not call view on_update
        self.view_update_first: bool | None = True
        # True will call view.on_resize before sections on_resize, False after,
        # None will not call view on_resize
        self.view_resize_first: bool | None = True

        # Events that the section manager should handle (instead of the View) if
        # sections are present in a View
        self.managed_events: set = {
            "on_mouse_motion",
            "on_mouse_drag",
            "on_mouse_press",
            "on_mouse_release",
            "on_mouse_scroll",
            "on_mouse_enter",
            "on_mouse_leave",
            "on_key_press",
            "on_key_release",
            "on_draw",
            "on_update",
            "on_resize",
        }

    @property
    def sections(self) -> list[Section]:
        """Property that returns the list of sections"""
        return self._sections

    @property
    def has_sections(self) -> bool:
        """Returns true if this section manager has sections"""
        return bool(self._sections)

    @property
    def is_current_view(self) -> bool:
        """
        Returns if this section manager view is the current on the view window
        a.k.a.: is the view that is currently being shown
        """
        return self.view.window.current_view is self.view

    def disable(self) -> None:
        """
        Disable all sections
        Disabling a section will trigger section.on_hide_section
        """
        for section in self._sections:
            section.enabled = False

    def enable(self) -> None:
        """
        Enables all sections
        Enabling a section will trigger section.on_show_section
        """
        for section in self._sections:
            section.enabled = True

    def get_section_by_name(self, name: str) -> Section | None:
        """
        Returns the first section with the given name
        :param name: the name of the section you want
        :return: the first section with the provided name. None otherwise
        """
        for section in self._sections:
            if section.name == name:
                return section
        return None

    def add_section(
        self,
        section: "Section",
        at_index: int | None = None,
        at_draw_order: int | None = None,
    ) -> None:
        """
        Adds a section to this Section Manager
        Will trigger section.on_show_section if section is enabled

        :param section: The section to add to this section manager
        :param at_index: Inserts the section at that index for event capture and update events.
                         If None at the end
        :param at_draw_order: Inserts the section in a specific draw order.
                              Overwrites section.draw_order
        """
        if not isinstance(section, Section):
            raise ValueError("You can only add Section instances")
        section._view = self.view  # modify view param from section
        if at_index is None:
            self._sections.append(section)
        else:
            self._sections.insert(at_index, section)
        # keep sections order updated in the lists of sections to draw
        self.sort_section_event_order()
        if at_draw_order is None:
            self.sort_sections_draw_order()
        else:
            section.draw_order = at_draw_order  # this will trigger self.sort_section_draw_order

        # trigger on_show_section if the view is the current one and section is enabled:
        if self.is_current_view and section.enabled:
            section.on_show_section()

    def remove_section(self, section: Section) -> None:
        """
        Removes a section from this section manager

        :param section: the section to remove
        """

        # trigger on_hide_section if the view is the current one and section is enabled
        if self.is_current_view and section.enabled:
            section.on_hide_section()

        section._view = None
        self._sections.remove(section)

        # keep sections order updated in the lists of sections
        self.sort_section_event_order()
        self.sort_sections_draw_order()

    def sort_section_event_order(self) -> None:
        """
        This will sort sections on event capture order (and update) based on
        insertion order and section.modal.
        """
        # modals go first
        self._sections.sort(key=lambda s: 0 if s.modal else 1)

    def sort_sections_draw_order(self) -> None:
        """This will sort sections on draw order based on section.draw_order and section.modal"""
        # modals go last
        self._sections_draw = sorted(
            self._sections, key=lambda s: math.inf if s.modal else s.draw_order
        )

    def clear_sections(self) -> None:
        """Removes all sections and calls on_hide_section for each one if enabled"""
        for section in self._sections:
            if section.enabled:
                section.on_hide_section()
            section._view = None
        self._sections = []
        self._sections_draw = []

    def on_update(self, delta_time: float) -> None:
        """
        Called on each event loop.

        :param delta_time: the delta time since this method was called last time
        """
        modal_present = False
        if self.view_update_first is True:
            self.view.on_update(delta_time)
        for section in self._sections:
            if section.enabled and not section.block_updates and not modal_present:
                section.on_update(delta_time)
                if section.modal:
                    modal_present = True
        if self.view_update_first is False:
            self.view.on_update(delta_time)

    def on_draw(self) -> None:
        """
        Called on each event loop to draw.

        It automatically calls camera.use() for each section that has a camera and
        resets the camera effects by calling the default SectionManager camera
        afterwards if needed. The SectionManager camera defaults to a camera that
        has the viewport and projection for the whole screen.
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

        :param width: the new width of the screen
        :param height: the new height of the screen
        """
        # The Default camera auto-resizes.
        if self.view_resize_first is True:
            self.view.on_resize(width, height)  # call resize on the view
        for section in self.sections:
            if section.enabled:
                section.on_resize(width, height)
        if self.view_resize_first is False:
            self.view.on_resize(width, height)  # call resize on the view

    def disable_all_keyboard_events(self) -> None:
        """Removes the keyboard event handling from all sections"""
        for section in self.sections:
            section.accept_keyboard_keys = False

    def get_first_section(self, x: int, y: int, *, event_capture: bool = True) -> Section | None:
        """
        Returns the first section based on x,y position

        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param event_capture: True will use event capture dimensions,
                              False will use section draw size
        :return: a section if match the params otherwise None
        """
        for section in self._sections:
            if section.enabled:
                if event_capture is True and section.should_receive_mouse_event(x, y):
                    return section
                if event_capture is False and section.mouse_is_on_top(x, y):
                    return section
        return None

    def get_sections(
        self, x: int, y: int, *, event_capture: bool = True
    ) -> Generator[Section, None, None]:
        """
        Returns a list of sections based on x,y position

        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param event_capture: True will use event capture dimensions,
                              False will use section draw size
        :return: a generator with the sections that match the params
        """
        for section in self._sections:
            if section.enabled:
                if event_capture is True and section.should_receive_mouse_event(x, y):
                    yield section
                if event_capture is False and section.mouse_is_on_top(x, y):
                    yield section

    def dispatch_mouse_event(
        self,
        event: str,
        x: int,
        y: int,
        *args,
        current_section: Section | None = None,
        **kwargs,
    ) -> bool | None:
        """
        Generic method to dispatch mouse events to the correct Sections

        :param event: the mouse event name to dispatch
        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param args: any other position arguments that should be delivered to the dispatched event
        :param current_section: the section this mouse event should be delivered to.
                                If None, will retrieve all
                                sections that should receive this event based on x, y coordinates
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """

        sections: list | Generator

        if current_section:
            # affected section is already pre-computed
            sections = [current_section]
        else:
            # get the sections from mouse position
            sections = self.get_sections(x, y)

        prevent_dispatch = EVENT_UNHANDLED
        prevent_dispatch_view = EVENT_UNHANDLED

        for section in sections:
            if prevent_dispatch is EVENT_HANDLED:
                break
            mouse_events_allowed = section.accept_mouse_events
            if mouse_events_allowed is False:
                continue
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

                    # mark prevent dispatch as handled if section is modal
                    prevent_dispatch = EVENT_HANDLED if section.modal else prevent_dispatch

                    # check if section prevents dispatching this event any further
                    # in the section stack
                    if prevent_dispatch is EVENT_HANDLED or any(
                        test in section.prevent_dispatch for test in [True, event]
                    ):
                        # prevent_dispatch attributte from section only affects if
                        #  the method is implemented in the same section
                        prevent_dispatch = EVENT_HANDLED

            if any(test in section.prevent_dispatch_view for test in [True, event]):
                # check if the section prevents dispatching events to the view
                prevent_dispatch_view = EVENT_HANDLED

        if prevent_dispatch_view is EVENT_UNHANDLED:
            # call the method from the view.
            method = getattr(self.view, event, None)  # get the method from the view
            if method:
                # call the view method
                prevent_dispatch_view = method(x, y, *args, **kwargs)
        return prevent_dispatch_view or prevent_dispatch

    def dispatch_keyboard_event(self, event: str, *args, **kwargs) -> bool | None:
        """
        Generic method to dispatch keyboard events to the correct sections

        :param event: the keyboard event name to dispatch
        :param args: any other position arguments that should be delivered to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
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
                        test in section.prevent_dispatch for test in [True, event]
                    ):
                        # prevent_dispatch attributes from section only affect
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

    def on_mouse_press(self, x: int, y: int, *args, **kwargs) -> bool | None:
        """
        Triggers the on_mouse_press event on the appropriate sections or view

        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param args: any other position arguments that should be delivered to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        return self.dispatch_mouse_event("on_mouse_press", x, y, *args, **kwargs)

    def on_mouse_release(self, x: int, y: int, *args, **kwargs) -> bool | None:
        """
        Triggers the on_mouse_release event on the appropriate sections or view

        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param args: any other position arguments that should be delivered to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        return self.dispatch_mouse_event("on_mouse_release", x, y, *args, **kwargs)

    def dispatch_mouse_enter_leave_events(
        self, event_origin: str, x: int, y: int, *args, **kwargs
    ) -> bool | None:
        """
        This helper method will dispatch mouse enter / leave events to sections
        based on 'on_mouse_motion' and 'on_mouse_drag' events.
        Will also dispatch the event (event_origin) that called this method

        :param event_origin: The mouse event name that called this method.
                             This event will be called here.
        :param x: The x axis coordinate
        :param y: The y axis coordinate
        :param args: Any other position arguments that should be delivered to the dispatched event
        :param kwargs: Any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        before_sections = self.mouse_over_sections
        current_sections = list(self.get_sections(x, y))  # consume the generator

        prevent_dispatch_origin = EVENT_UNHANDLED  # prevent dispatch for the origin mouse event

        prevent_dispatch_el = EVENT_UNHANDLED  # prevent dispatch for enter/leave events
        for section in before_sections:
            if section not in current_sections:
                if prevent_dispatch_el is EVENT_HANDLED:
                    break
                # dispatch on_mouse_leave to before_section
                prevent_dispatch_el = self.dispatch_mouse_event(
                    "on_mouse_leave", x, y, current_section=section
                )

        prevent_dispatch_el = EVENT_UNHANDLED
        for section in current_sections:
            if section not in before_sections:
                if prevent_dispatch_el is EVENT_UNHANDLED:
                    # dispatch on_mouse_enter to current_section
                    prevent_dispatch_el = self.dispatch_mouse_event(
                        "on_mouse_enter", x, y, current_section=section
                    )
            if prevent_dispatch_origin is EVENT_UNHANDLED:
                prevent_dispatch_origin = self.dispatch_mouse_event(
                    event_origin, x, y, *args, **kwargs
                )

        # at the end catch the sections the mouse is moving over
        self.mouse_over_sections = current_sections

        # NOTE: the result from mouse enter/leave events is ignored here
        return prevent_dispatch_origin

    def on_mouse_motion(self, x: int, y: int, *args, **kwargs) -> bool | None:
        """
        This method dispatches the on_mouse_motion and also calculates if
        on_mouse_enter/leave should be fired.

        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param args: any other position arguments that should be deliverd to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        return self.dispatch_mouse_enter_leave_events("on_mouse_motion", x, y, *args, **kwargs)

    def on_mouse_drag(self, x: int, y: int, *args, **kwargs) -> bool | None:
        """
        This method dispatches the on_mouse_drag and also calculates if
        on_mouse_enter/leave should be fired.

        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param args: any other position arguments that should be delivered to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        return self.dispatch_mouse_enter_leave_events("on_mouse_drag", x, y, *args, **kwargs)

    def on_mouse_scroll(self, x: int, y: int, *args, **kwargs) -> bool | None:
        """
        Triggers the on_mouse_scroll event on the appropriate sections or view

        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param args: any other position arguments that should be deliverd to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        return self.dispatch_mouse_event("on_mouse_scroll", x, y, *args, **kwargs)

    def on_mouse_enter(self, x: int, y: int, *args, **kwargs) -> bool | None:
        """
        Triggered when the mouse enters the window space
        Will trigger on_mouse_enter on the appropriate sections or view

        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param args: any other position arguments that should be delivered to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        current_sections = list(self.get_sections(x, y))  # consume the generator

        # set the sections the mouse is over
        self.mouse_over_sections = current_sections

        prevent_dispatch = EVENT_UNHANDLED
        for section in current_sections:
            if prevent_dispatch is EVENT_HANDLED:
                break
            prevent_dispatch = self.dispatch_mouse_event(
                "on_mouse_enter", x, y, *args, **kwargs, current_section=section
            )
        return prevent_dispatch

    def on_mouse_leave(self, x: int, y: int, *args, **kwargs) -> bool | None:
        """
        Triggered when the mouse leaves the window space
        Will trigger on_mouse_leave on the appropriate sections or view

        :param x: the x axis coordinate
        :param y: the y axis coordinate
        :param args: any other position arguments that should be delivered to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        prevent_dispatch = EVENT_UNHANDLED
        for section in self.mouse_over_sections:
            if prevent_dispatch is EVENT_HANDLED:
                break
            prevent_dispatch = self.dispatch_mouse_event(
                "on_mouse_leave", x, y, *args, **kwargs, current_section=section
            )
        # clear the sections the mouse is over as it's out of the screen
        self.mouse_over_sections = []
        return prevent_dispatch

    def on_key_press(self, *args, **kwargs) -> bool | None:
        """
        Triggers the on_key_press event on the appropriate sections or view

        :param args: any other position arguments that should be delivered to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        return self.dispatch_keyboard_event("on_key_press", *args, **kwargs)

    def on_key_release(self, *args, **kwargs) -> bool | None:
        """
        Triggers the on_key_release event on the appropriate sections or view

        :param args: any other position arguments that should be delivered to the dispatched event
        :param kwargs: any other keyword arguments that should be delivered to the dispatched event
        :return: EVENT_HANDLED or EVENT_UNHANDLED, or whatever the dispatched method returns
        """
        return self.dispatch_keyboard_event("on_key_release", *args, **kwargs)

    def on_show_view(self) -> None:
        """
        Called when the view is shown
        The View.on_show_view is called before this by the Window.show_view method
        """
        for section in self.sections:
            if section.enabled:
                section.on_show_section()

    def on_hide_view(self) -> None:
        """
        Called when the view is hide
        The View.on_hide_view is called before this by the Window.hide_view method
        """
        for section in self.sections:
            if section.enabled:
                section.on_hide_section()
