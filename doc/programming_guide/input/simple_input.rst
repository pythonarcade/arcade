.. _pg_simple_input:

Simple Input
============

This section will cover simple input handling in Arcade, which consists of just keyboard/mouse devices.

There are two possible approaches to this to be aware of:

* Event Based
* Polling

These two approaches work somewhat different, and will require different levels of code on your end to handle them.
However these approaches are not mutually exclusive, you can use both at the same time for different purposes where
one might be preferable to the other.

Event Based
-----------

With the event based approach, your game will register handlers that Arcade will call whenever an input happens.

For example, when you press the ``A`` button on your keyboard, Arcade would send an event to any registered handlers
for key press events. And then similarly when the key is released, Arcade will send an event to handlers registered for
key release events.

Using this system if you want to know if a button is currently held down, it would be up to your application to track the
state of the ``A`` key, changing it when your handlers receive a call for press and release events.

Polling
-------

In contrast to the event based approach where Arcade notifies your application of input events, polling is the opposite way
around. With polling you can ask Arcade at any point in time what the state of a given key or mouse button is. This can be
useful when you want to modify some action that is being taken based on if a certain key is currently pressed or not, but
if you rely exclusively on polling, you may not always respond immediately to input actions if you don't poll often enough.

Whereas with the event based approach, Arcade will trigger your handlers immediately when the event happens.

Keyboard
--------

.. _pg_simple_input_keyboard:

How do I handle keyboard events?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You must implement key event handler functions. These functions are called whenever a
key event is detected:

* :meth:`arcade.Window.on_key_press`
* :meth:`arcade.Window.on_key_release`

You need to implement your own versions of the above methods on your subclass
of :class:`arcade.Window`. The :ref:`arcade.key <key>` module contains
constants for specific keys.

For runnable examples, see the following, and look for the ``on_key_press`` and ``on_key_release`` functions:

* :ref:`sprite_move_keyboard`
* :ref:`sprite_move_keyboard_better`
* :ref:`sprite_move_keyboard_accel`

.. note:: If you are using :class:`Views <arcade.View>`, you can
          also implement key event handler methods on them.

How do I poll for keyboard state?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you need to ask Arcade what the state of a given key is, you can do so through your :class:`arcade.Window` class.

.. code-block:: python

    import arcade

    window = arcade.get_window()
    a_key_pressed = window.keyboard[arcade.keys.A]
    if a_key_pressed:
        print("The A key is pressed")

Modifiers
^^^^^^^^^

.. _pg_simple_input_keyboard_modifiers:

What is a modifier?
^^^^^^^^^^^^^^^^^^^

Modifiers are keys that modify the behavior of keyboard input. Examples include
keys such as shift, control, and command. Lock keys such as capslock are also
modifiers.

What does active mean?
^^^^^^^^^^^^^^^^^^^^^^

Modifiers can be active in two ways:

1. A modifier key is currently held down by the user (example: shift)
2. A lock modifier is currently turned on (example: capslock)

This is important because lock modifiers can be active without their
corresponding key held down. Instead, they are switched on and off by pressing
their keys.

How do I use modifiers?
^^^^^^^^^^^^^^^^^^^^^^^

As long as you don't need to distinguish between the left and right versions of
modifiers keys, you can rely on the ``modifiers`` argument of :ref:`key event
handlers <pg_simple_input_keyboard>`.

For every key event, the current state of all modifiers is passed to the
handler method through the ``modifiers`` argument as a single integer. For each
active modifier during an event, a corresponding bit is set to 1.

Constants for each of these bits are defined in :ref:`arcade.key <key>`:

.. code-block:: text

    MOD_SHIFT
    MOD_CTRL
    MOD_ALT         Not available on Mac OS X
    MOD_WINDOWS     Available on Windows only
    MOD_COMMAND     Available on Mac OS X only
    MOD_OPTION      Available on Mac OS X only
    MOD_CAPSLOCK
    MOD_NUMLOCK
    MOD_SCROLLLOCK
    MOD_ACCEL       Equivalent to MOD_CTRL, or MOD_COMMAND on Mac OS X.

You can use these constants with bitwise operations to check if a specific
modifier is active during a keyboard event:

.. code-block:: python

    # this should be implemented on a subclass of Window or View
    def on_key_press(self, symbol, modifiers):

        if modifiers & arcade.key.MOD_SHIFT:
            print("The shift key is held down")

        if modifiers & arcade.key.MOD_CAPSLOCK:
            print("Capslock is on")

How do I tell left & right modifers apart?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Many keyboards have both left and right versions of modifiers such as shift and
control. However, the ``modifiers`` argument to key handlers does not tell you which
specific modifier keys are currently pressed!

Instead, you have to use specific key codes for left and right versions from
:ref:`arcade.key <key>` to :ref:`track press and release events
<pg_simple_input_keyboard>`.
