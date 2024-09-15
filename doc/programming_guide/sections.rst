.. _sections:

Sections
========

In a simple game, the whole viewport is used to display the game "map".
In more advanced games it's fairly normal to have this viewport divided into
different "sections" with different usages. Areas where different information is
displayed and processed. For example you can have a menu at the top, some info
panel at the right and the game main "screen" (the "map") covering the rest of
the viewport.

To achieve this separation of game logic you have Sections.
A :class:`~arcade.Section` is a way to divide a :class:`~arcade.View` space into smaller parts,
each one will then receive events redirected depending on configuration and the
space of the view occupied.
Sections can isolate code that otherwise goes packed together in a :class:`~arcade.View`
. This way the code remains exactly where it belongs and not mixed together with
code from other parts of the program.

By configuring a :class:`~arcade.Section` you can capture some events or for example only
capture certain keys from keyboard events. Also you can configure which
events are propagated to other underlying sections or even to the view itself.

Sections can also be "modal" meaning that they will capture all the events
first but draw last and also will prevent other views from receiving the
``on_update`` event.

Also note that if you don't use sections in your code, nothing changes. Even
the :class:`~arcade.SectionManager` is not created if you don't add sections.

**Key features of Sections:**

 - Divide the screen into logical components (Sections).
 - Event dispatching: a :class:`~arcade.Section` will capture mouse events based on the space occupied from the view. Also keyboard events will be captured based on configuration.
 - Prevent dispatching: a :class:`~arcade.Section` can be configured to prevent dispatching events captured or let events flow to other sections underneath.
 - Event capturing order: based on a :class:`~arcade.Section` insertion order you can configure the order in which sections will capture events.
 - Draw order: you can configure the order in which sections are drawn (sections can overlap!).
 - :class:`~arcade.Section` "enable" property to show or hide sections. You can toggle that.
 - Modal Sections: sections that draw last but capture all events and also stop
   other sections from updating.
 - Automated camera swich: Sections will try to activate and deactivate cameras when changing between sections.


**Important: You don't need to cover 100% of the View with sections. Sections**
**can work with the View as well. Also, Sections can overlap.**


A simple example
----------------

A small program without the use of sections needs to perform some checks
inside a ``on_mouse_release`` event to know what to do depending on the mouse
position.

For example maybe if the mouse is on top of the map you want to do something,
but if the mouse is somewhere else you may need to do other things.

This is what this somehow looks without sections:

.. code:: py

    class MyView(arcade.View):
        # ...

        def on_mouse_release(x: int, y: int, *args, **kwargs):
            if x > 700:
                # click in the side
                do_some_logic_when_side_clicking()
            else:
                # click on the game map
                do_something_in_the_game_map()


This code can and often become long and with a lot of checks to know what to do.

By using Sections, you can improve this code and automate this simple checks.

This is what looks like using Sections:


.. code:: py

    import arcade

    class Map(arcade.Section):

        # ...

        def on_mouse_release(x: int, y: int, *args, **kwargs):
            # clicks on the map are handled here
            pass


    class Side(arcade.Section):

        # ...

        def on_mouse_release(x: int, y: int, *args, **kwargs):
            # clicks on the side of the screen are handled here
            pass


    class MyView(arcade.View):

        def __init__(self, *args, **kwargs):
            self.map_section = Map(0, 0, 700, self.window.height)
            self.side_section = Side(700, 0, 100, self.window.height)

            self.sm = arcade.SectionManager()
            self.sm.add_section(self.map_section)
            self.sm.add_section(self.side_section)

        def on_show_view(self) -> None:
            self.sm.enable()

        def on_hide_view(self) -> None:
            self.sm.disable()

        # ...


How to work with Sections
-------------------------

To work with sections you first need to have a :class:`~arcade.View`. Sections depend on
Views and are handled by a special :class:`~arcade.SectionManager` inside the
:class:`~arcade.View`. The :class:`~arcade.SectionManager` will handle all the events and
dispatch them to the sections. The :class:`~arcade.SectionManager` will also handle the
drawing order of the sections.

You will have to enable and disable the :class:`~arcade.SectionManager` in the :class:`~arcade.View`
``on_show_view`` and ``on_hide_view`` methods.

To create a :class:`~arcade.Section` start by inheriting from :py:class:`~arcade.Section`.

Based on the :class:`~arcade.Section` configuration your section will start receiving
events from the View :class:`~arcade.SectionManager`. A :class:`~arcade.Section` has all the
events a :class:`~arcade.View` has like ``on_draw``, ``on_update``, ``on_mouse_press``,
etc.

On instantiation define the positional arguments (left, bottom, width, height)
of the section. These are very important properties of a :class:`~arcade.Section`: as they
define the event capture rectangular area.


Properties of a :class:`~arcade.Section`:

**position: (left, bottom, width, height)**:
    This are mandatory arguments that you need to provide when instantiating a
    :class:`~arcade.Section`. This is very important as this rectangular positioning
    will determine the event capture space for mouse related events.
    This also will help you determine inside a class the space that is
    holding for example when you want to draw something or calculate coordinates.

**name:**
    A :class:`~arcade.Section` can optionally get a name so it will be easier to
    debug and identify what Section is doing what. When logging for example
    is very nice to log the :class:`~arcade.Section` name at the beginning so you
    have a reference from where the log was generated.

**accept_keyboard_keys:**
    This allows to tell if a :class:`~arcade.Section` can receive keyboard events
    (accept_keyboard_keys=False) or to tell which keyboard keys are captured
    in this :class:`~arcade.Section` (accept_keyboard_keys={arade.key.UP, arcade.key.DOWN})

**accept_mouse_events:**
    This allows to tell if a :class:`~arcade.Section` can receive mouse events or which
    mouse events are accepted.
    For example: accept_mouse_events={'on_mouse_move'} means only mouse move events
    will be captured.

**prevent_dispatch:**
    This tells a :class:`~arcade.Section` if it should prevent the dispatching of certain
    events to other sections down event capture stream. By default a :class:`~arcade.Section`
    will prevent dispatching all handled events.
    By passing ``prevent_dispatch={'on_mouse_press'}`` all events will propagate
    down the event capture stream except the ``on_mouse_press`` event.
    Note that passing ``prevent_dispatch=None`` (the default) is the same as passing
    ``prevent_dispatch={True}`` which means "prevent all events" from dispatching to other sections.
    You can also set ``prevent_dispatch={False}`` to dispatch all events to other sections.

**prevent_dispatch_view:**
    This allows to tell a :class:`~arcade.Section` if events (and what events) should
    not be dispatched to the underlying :class:`~arcade.View`.
    This is handy if you want to do some action in the :class:`~arcade.View` code whether
    or not the event was handled by another :class:`~arcade.Section`. By default a
    :class:`~arcade.Section` will prevent dispatching all handled events to the :class:`~arcade.View`.
    Note that passing ``prevent_dispatch=None`` (the default) is the same as passing
    ``prevent_dispatch={True}`` which means "prevent all events" from dispatching to the view.
    You can also set ``prevent_dispatch={False}`` to dispatch all events to other sections.
    **Also note that in order for the view to receive any event, ALL the sections need to allow
    the dispatch of that particular event. If at least one section prevents it, the event will not
    be delivered to the view.**

**local_mouse_coordinates:**
    If True the section mouse events will receive x, y coordinates section
    related to the section dimensions and position (not related to the screen).
    **Note that although this seems very useful, section local coordinates doesn't work with
    Arcade collision methods. You can use Section ``get_xy_screen_relative`` to transform local
    mouse coordinates to screen coordinates that work with Arcade collision methods**

**enabled:**
    By default all sections are enabled. This allows to tell if this particular
    :class:`~arcade.Section` should be enabled or not. If a :class:`~arcade.Section` is not
    enabled, it will not capture any event, draw, update, etc. It will be
    as it didn't exist.
    You can enable and disable sections at any time allowing some cool effects.
    Nota that setting this property will trigger the section ``on_show_section`` or ``on_hide_section`` events.

**modal:**
    This tells the :class:`~arcade.SectionManager` that this :class:`~arcade.Section` is modal.
    This means that the :class:`~arcade.Section` will capture all events first and not
    deliver any events to the underlying sections or view. Also, It will draw
    last (on top of other ``on_draw`` calls). When enabled a modal :class:`~arcade.Section`
    will prevent all other sections from receive ``on_update`` events.

**draw_order:**
    This allows to define the draw order this :class:`~arcade.Section` will have.
    The lower the number the earlier this section will get draw.
    This is handy when you have overlapping sections and you want some
    :class:`~arcade.Section` to be drawn on top of another.
    By default sections will be draw in the order they are added (except modal
    sections which no matter what will be drawn last).
    Note that this can be different from the event capture order or the on_update order
    which is defined by the insertion order in the :class:`~arcade.SectionManager`.

Other handy :class:`~arcade.Section` properties:

- block_updates: if True this section will not have the ``on_update`` method called.
- camera: this is meant to hold a ``arcade.Camera`` but it is None by default. The SectionManager will trigger the use of the camera when is needed automatically.

Handy :class:`~arcade.Section`: methods:

- overlaps_with: this will tell if another :class:`~arcade.Section` overlaps with this one.
- mouse_is_on_top: this will tell if given a x, y coordinate, the mouse is on top of the section.
- get_xy_screen_relative: get screen x, y coordinates from x, y section coordinates.
- get_xy_section_relative: get section x, y coordinates from x, y screen coordinates.


Sections configuration and logic with an example
------------------------------------------------

Imagine a game where you have this basic components:

- A 800x600 screen viewport
- A game map
- A menu bar at the top of the screen
- A side right panel with data from the game
- Popup messages (dialogs)

With this configuration you can divide this logic into sections with a some
configuration.

Lets look what this configuration may look:

.. code:: py

    import arcade


    class Map(arcade.Section):
        #... define all the section logic


    class Menu(arcade.Section):
        #... define all the section logic


    class Panel(arcade.Section):
        #... define all the section logic


    class PopUp(arcade.Section):
        def __init__(message, *args, **kwargs):
            super().__init(*args, **kwargs)
            self.message = message

        # define draw logic, etc...


    class MyView(arcade.View):

        def __init__(self, *args, **kwargs):
            self.map = Map(left=0, bottom=0, width=600, height=550,
                           name='Map', draw_order=2)
            self.menu = Menu(left=0, bottom=550, width=800, height=50,
                             name='Menu', accept_keyboard_keys=False,
                             accept_mouse_events={'on_mouse_press'})
            self.panel = Panel(left=600, bottom=0, width=200, height=550,
                                name='Panel', accept_keyboard_keys=False,
                                accept_mouse_events=False)

            popup_left = (self.view.window.width // 2) - 200
            popup_bottom = (self.view.window.height // 2) - 100
            popup_width = 400
            popup_height = 200
            self.popup = PopUp(message='', popup_left, popup_bottom, popup_width,
                               popup_height, enabled=False, modal=True)

            self.sm = arcade.SectionManager()
            self.sm.add_section(self.map)
            self.sm.add_section(self.menu)
            self.sm.add_section(self.panel)
            self.sm.add_section(self.popup)

        def on_show_view(self) -> None:
            self.sm.section_manager.enable()

        def on_hide_view(self) -> None:
            self.sm.section_manager.disable()

        def close():
            self.popup.message = 'Are you sure you want to close the view?'
            self.popup.enabled = True


Lets go step by step.
First we configure a Map section that will hold the map. This Section will start at
left, bottom = 0,0 and will not occupy the whole screen.
Mouse events that occur outside of this coordinates will not be handled by the Map
event handlers. So Map will only need to take care of what happens inside the map.

Second we configure a Menu section that will hold some buttons. This menu takes the top
space of the screen that the Map has left. The Map + the Menu will occupy 100% of the height
of the screen. The menu section is configured to not receive any keyboard events and
to only receive on_mouse_press events, ignoring all other type of mouse events.

Third, the Panel also doesn't receive keyboard events. So the Map is the only handling
keyboard events at the moment. Also no mouse events are allowed in the panel.
This panel is just to show data.

For the last part notice that we define a section that it will be disabled at first
and that is modal. This section will render something with a message.
The section is used when the close method of the view is called. Because PopUp is a
modal section, when enabled it's rendered on top of everything. Also, all other
section stoped updating and all events are captured by the modal section.
So in brief we are "stopping" the world outside the popup section.


Section Unique Events
---------------------

There a few unique events that belong to sections and are somehow special in the way they are triggered:

* ``on_mouse_enter`` and ``on_mouse_leave``:
    These events are triggered on two occasions: when the mouse enters/leaves the
    view and when the :class:`~arcade.SectionManager` detects by mouse motion (or dragging)
    that the mouse has enter / leaved the section dimensions.

* ``on_show_section`` and ``on_hide_section``:
    There events are triggered only when the section **is enabled** and under
    certain circumstances that must be known:

    - When the section is added or removed from the :class:`~arcade.SectionManager` and the :class:`~arcade.View` is currently being shown
    - When the section is enabled or disabled
    - When Window calls ``on_show_view`` or ``on_hide_view``


The Section Manager
-------------------

Behind the scenes, when sections are added to the :class:`~arcade.View` the
:class:`~arcade.SectionManager` is what will handle all events instead of
the :class:`~arcade.View` itself.

Usually you won't need to work with the :class:`~arcade.SectionManager`, but there are
some cases where you will need to work with it.

You add sections usually with ``View.add_section`` but the same method exists on
the :class:`~arcade.SectionManager`. Also you have a ``remove_section`` and a
``clear_sections`` method.

You can ``enable`` or  ``disable`` the :class:`~arcade.SectionManager` to completely
enable or disable all sections at once.

There are some other functionality exposed from the :class:`~arcade.SectionManager` like
``get_section_by_name`` that can also be useful. Check the api to know about those.

Also there are three attributes that can be configured in the :class:`~arcade.SectionManager`
that are useful and important sometimes.

By default, ``on_draw``, ``on_update`` and ``on_resize`` are events that will always
be triggered in the :class:`~arcade.View` before any section has triggered them.
This is the default but you can configure this with the following attributes:

- ``view_draw_first``
- ``view_update_first``
- ``view_resize_first``

Both three work the same way:

- True (default) to trigger that event in the :class:`~arcade.View` before the sections.
- False so it's triggered in the :class:`~arcade.View` after sections corresponding methods.
- None to not trigger that event in the :class:`~arcade.View` at all.
