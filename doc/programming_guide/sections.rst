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
A :class:`Section` is a way to divide a :class:`View` space into smaller parts,
each one will then receive events redirected depending on configuration and the
space of the view occupied.
Sections can isolate code that otherwise goes packed together in a :class:`View`
. This way the code remains exactly where it belongs and not mixed together with
code from other parts of the program.

By configuring a :class:`Section` you can capture some events or for example only
capture certain keys from keyboard events. Also you can configure which
events are propagated to other underlying sections or even to the view itself.

Sections can also be "modal" meaning that they will capture all the events
first but draw last and also will prevent other views from receiving the
``on_update`` event.

Also note that if you don't use sections in your code, nothing changes. Even
the :class:`SectionManager` is not created if you don't add sections.

**Key features of Sections:**

 - Divide the screen into logical components (Sections).
 - Event dispatching: a :class:`Section` will capture mouse events based on the space occupied from the view. Also keyboard events will be captured based on configuration.
 - Prevent dispatching: a :class:`Section` can be configured to prevent dispatching events captured or let events flow to other sections underneath.
 - Event capturing order: based on a :class:`Section` insertion order you can configure the order in which sections will capture events.
 - Draw order: you can configure the order in which sections are drawn (sections can overlap!).
 - :class:`Section` "enable" property to show or hide sections. You can toogle that.
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

By using Sections this is what looks like:


.. code:: py

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
            self.side_section = SideSpace(700, 0, 100, self.window.height)

            self.add_section(self.map_section)
            self.add_section(self.side_section)

        # ...


How to work with Sections
-------------------------

To work with sections you first need to have a :class:`View`. Sections depend on
Views and are handled by a special :class:`SectionManager` inside the
:class:`View`. Don't worry, 99% of the time you won't need to interact with the
:class:`SectionManager`.

To create a :class:`Section` start by inheriting from ``arcade.Section``.

Based on the :class:`Section` configuration your section will start receiving
events from the View :class:`SectionManager`. A :class:`Section` has all the
events a :class:`View` has like ``on_draw``, ``on_update``, ``on_mouse_press``,
etc.

On instantiation define the positional arguments (left, bottom, width, height)
of the section. These are very important properties of a :class:`Section`: as they
define the event capture rectangular area.


Properties of a :class:`Section`:

**position: (left, bottom, width, height)**:
    This are mandatory arguments that you need to provide when instantiating a
    :class:`Section`. This is very important as this rectangular positioning
    will determine the event capture space for mouse related events.
    This also will help you determine inside a class the space that is
    holding for example when you want to draw something or calculate coordinates.

**name:**
    A :class:`Section` can optionally get a name so it will be easier to
    debug and indetify what Section is doing what. When logging for example
    is very nice to log the :class:`Section` name at the beginnig so you
    have a reference from where the log was generated.

**accept_keyboard_keys:**
    This allows to tell if a :class:`Section` can receive keyboard events
    (accept_keyboard_keys=False) or to tell which keyboard keys are captured
    in this :class:`Section` (accept_keyboard_keys={arade.key.UP, arcade.key.DOWN})

**accept_mouse_events:**
    This allows to tell if a :class:`Section` can receive mouse events or which
    mouse events are accepted.
    For example: accept_mouse_events={'on_mouse_move'} means only mouse move events
    will be captured.

**prevent_dispatch:**
    This tells a :class:`Section` if it should prevent the dispatching of certain
    events to other sections down event capture stream. By default a :class:`Section`
    will prevent dispatching all handled events.
    By passing ``prevent_dispatch={'on_mouse_press'}`` all events will propagate
    down the event capture stream except the ``on_mouse_press`` event.

**prevent_dispatch_view:**
    This allows to tell if a :class:`Section` if events (and what events) should
    not be dispatched to the underlying :class:`View`.
    This is handy if you want to do some action in the :class:`View` code whether
    or not the event was handled by another :class:`Section`. By default a
    :class:`Section` will prevent dispatching all handled events to the :class:`View`.

**local_mouse_coordinates:**
    If True the section mouse events will receive x, y coordinates section
    related to the section dimensions and position (not related to the screen).

**enabled:**
    By default all sections are enabled. This allows to tell if this particuar
    :class:`Section` should be enabled or not. If a :class:`Section` is not
    enabled, it will not capture any event, draw, update, etc. It will be
    as it didn't exist.
    You can enable and disable sections at any time allowing some cool efects.

**modal:**
    This tells the :class:`SectionManager` that this :class:`Section` is modal.
    This means that the :class:`Section` will capture all events first and not
    deliver any events to the underlying sections or view. Also, It will draw
    last (on top of other ``on_draw`` calls). When enabled a modal :class:`Section`
    will prevent all other sections from receive ``on_update`` events.

**draw_order:**
    This allows to define the draw order this :class:`Section` will have.
    This is handy when you have overlaping sections and you want some
    :class:`Section` to be drawn ontop of another.
    By default sections will be draw in the order they are added (except modal
    sections).

Other handy :class:`Section` properties:

- block_updates: if True this section will not have the ``on_update`` method called.
- camera: this is meant to hold a ``arcade.Camera`` but it is None by default. The SectionManager will trigger the use of the camera when is needed automatically.

Handy :class:`Section`: methods:

- overlaps_with: this will tell if another :class:`Section` overlaps with this one.
- mouse_is_on_top: this will tell if given a x, y coodinate, the mouse is on top of the section.
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

        def close():
            self.popup.message = 'Are you sure you want to close the view?'
            self.popup.enabled = True


Lets go step by step.
First we configure a Map section that will hold the map. This Section will start at
left, bottom = 0,0 and will not occupy the whole screen.
Mouse events that occur outside of this coordinates will not be handled by the Map
event handlers. So Map will only needs to take care of what happens inside the map.

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

**``on_mouse_enter`` and ``on_mouse_leave``:**
    These events are triggered on two ocasions: when the mouse enters/leaves the
    view and when the :class:`SectionManager` detects by mouse motion (or dragging)
    that the mouse has enter / leaved the section dimensions.

**``on_show_section`` and ``on_hide_section``:**
    There events are triggered only when the section is enabled and under
    certain circumstances that must be known:
    - When the section is added or removed from the :class:`SectionManager` and the :class:`View` is currently being shown
    - When the section is enabled or disabled
    - When Window calls ``on_show_view`` or ``on_hide_view``


The Section Manager
-------------------

Behind the scenes, when sections are added to the :class:`View` the
:class:`SectionManager` is what will handle all events instead of
the :class:`View` itself.

You can access the :class:`SectionManager` by accessing the ``View.section_manager``.

Usually you won't need to work with the :class:`SectionManager`, but there are
some cases where you will need to work with it.

You add sections usually with ``View.add_section`` but the same method exists on
the :class:`SectionManager`. Also you have a ``remove_section`` and a
``clear_sections`` method.

You can ``enable`` or  ``disable`` the :class:`SectionManager` to completely
enable or disable all sections at once.

There are some other functionality exposed from the :class:`SectionManager` like
``get_section_by_name`` that can also be useful. Check the api to know about those.

Also there are three attributes that can be configured in the :class:`SectionManager`
that are useful and important sometimes.

By default, ``on_draw``, ``on_update`` and ``on_resize`` are events that will always
be triggered in the :class:`View` before the any section has triggered them.
This is the default but you can configure this with the following attributes:

-``view_draw_first``
-``view_update_first``
-``view_resize_first``

Both three work the same way:

- True (default) to trigger that event in the :class:`View` before the sections.
- False so it's triggered in the :class:`View` after sections corresponding methods.
- None to not trigger that event in the :class:`View` at all.
