.. _windows_and_views:

Windows and Views
=================

Every Arcade game has one :py:class:`arcade.Window`. It's the window on
your screen, and it receives events such as key presses, mouse movement,
and the regular calls to update and draw.

A :py:class:`arcade.View` is one screen of your game, such as a menu,
the game itself, a pause screen or a game over screen. The window shows
one view at a time and passes its events to that view.

The Window
----------

Create one window when your program starts:

.. code-block:: python

    window = arcade.Window(1280, 720, "My Game")

Some useful arguments and methods:

* ``fullscreen=True`` opens the window full screen.
  :py:meth:`~arcade.Window.set_fullscreen` switches while the game runs.
  See the :ref:`full_screen_example` example.
* ``resizable=True`` lets the player resize the window.
  See the :ref:`resizable_window` example.
* ``update_rate`` and ``draw_rate`` set how often ``on_update`` and
  ``on_draw`` are called, 60 times a second by default.
  :py:meth:`~arcade.Window.set_update_rate` and
  :py:meth:`~arcade.Window.set_draw_rate` change them later.
* :py:attr:`~arcade.Window.background_color` is the color
  :py:meth:`~arcade.Window.clear` fills the window with.

For how often each event is called and how time is measured, see
:doc:`event_loop`.

You can put a whole game in a :py:class:`~arcade.Window` subclass by
overriding its ``on_draw``, ``on_update`` and input methods. That's fine
for a small program with one screen.

Why Use Views?
--------------

With several screens in one window, ``on_draw`` and every input method
need to check which screen is showing:

.. code-block:: python

    def on_draw(self):
        self.clear()
        if self.state == "menu":
            ...
        elif self.state == "playing":
            ...
        elif self.state == "game_over":
            ...

A view keeps each screen in its own class instead. A view has the same
event methods as a window, such as ``on_draw``, ``on_update``,
``on_key_press`` and ``on_mouse_press``, and only the view being shown
gets them:

.. code-block:: python

    class MenuView(arcade.View):
        def on_draw(self):
            self.clear()
            arcade.draw_text("Press any key to start", 100, 100)

        def on_key_press(self, symbol, modifiers):
            self.window.show_view(GameView())


    class GameView(arcade.View):
        def on_draw(self):
            self.clear()
            ...  # Draw the game


    window = arcade.Window(1280, 720, "My Game")
    window.show_view(MenuView())
    arcade.run()

Inside a view, ``self.window`` is the window showing it.

Showing Views
-------------

:py:meth:`window.show_view(view) <arcade.Window.show_view>` switches to
a view. Before it returns, it:

#. Calls :py:meth:`~arcade.View.on_hide_view` on the view that was
   showing, if there was one, and stops sending it events.
#. Calls :py:meth:`~arcade.View.on_show_view` on the new view, and starts
   sending it events.

The next frame is drawn by the new view.
:py:attr:`window.current_view <arcade.Window.current_view>` is the view
being shown, and :py:meth:`~arcade.Window.hide_view` hides it without
showing another.

A view can be shown, hidden, and shown again. ``__init__`` runs once,
when you create the view, but ``on_show_view`` runs **every time** it's
shown. So:

* Put things that should happen once in ``__init__``, such as loading
  sprites and sounds.
* Put things that should happen each time the player arrives in
  ``on_show_view``, such as starting music, or resetting a menu's
  selection.
* Undo them in ``on_hide_view``, such as stopping music.

For example, a pause screen can keep the game view and show it again, so
the game continues where it left off:

.. code-block:: python

    class PauseView(arcade.View):
        def __init__(self, game_view):
            super().__init__()
            self.game_view = game_view

        def on_key_press(self, symbol, modifiers):
            if symbol == arcade.key.ESCAPE:
                # The same GameView object, so nothing is reset
                self.window.show_view(self.game_view)

To start a level over instead, show a new view: ``GameView()``.

How Events Reach a View
-----------------------

When the window gets an event, it calls the view's method first, then the
window's own method with the same name.

If you subclass :py:class:`~arcade.Window` and also use views, the
window's methods still run while a view is showing. For example, a
window ``on_draw`` that draws a score draws it on top of every view.
To stop the window's method from running for one event, return ``True``
from the view's method:

.. code-block:: python

    class GameView(arcade.View):
        def on_key_press(self, symbol, modifiers):
            if symbol == arcade.key.SPACE:
                self.player.jump()
                return True  # The window doesn't get this key press

Most games that use views use :py:class:`~arcade.Window` itself, without
subclassing it, so this doesn't come up.

Resizing
--------

Only the view being shown gets ``on_resize``. If the window is resized
while a view is hidden, the view isn't told. Cameras that match the
window size should be updated when the view is shown again:

.. code-block:: python

    def on_show_view(self):
        self.camera.match_window()

    def on_resize(self, width, height):
        self.camera.match_window()

See :doc:`camera` for more on cameras.

Background Color
----------------

Each view can have its own background color.
:py:meth:`View.clear() <arcade.View.clear>` uses the view's
:py:attr:`~arcade.View.background_color` if it has one, and the window's
otherwise:

.. code-block:: python

    class MenuView(arcade.View):
        def __init__(self):
            super().__init__(background_color=arcade.color.DARK_BLUE)

        def on_draw(self):
            self.clear()  # Fills with dark blue

GUI Views
---------

:py:class:`arcade.gui.UIView` is a view with a
:py:class:`~arcade.gui.UIManager` in ``self.ui``. It turns the GUI on in
``on_show_view`` and off in ``on_hide_view``, so buttons only respond
while the view is showing. If you override either method, call
``super().on_show_view()`` or ``super().on_hide_view()`` so this still
happens. See :ref:`gui` to learn more.

Learn More
----------

* :ref:`view-tutorial`: a tutorial adding instruction and game over
  screens to a game
* :ref:`view_screens_minimal`, :ref:`view_pause_screen` and
  :ref:`view_instructions_and_game_over`: examples
* :ref:`sections`: splitting one view into areas that each get their own
  events
