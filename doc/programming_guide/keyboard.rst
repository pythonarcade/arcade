Keyboard
========

.. _keyboard_events:

Events
------

What is a keyboard event?
^^^^^^^^^^^^^^^^^^^^^^^^^

Keyboard events are arcade's representation of physical keyboard interactions.

For example, if your keyboard is working correctly and you type the letter A
into the window of a running arcade game, it will see two separate events:

#. a key press event with the key code for ``A``
#. a key release event with the key code for ``A``

.. _keyboard_event_handlers:

How do I handle keyboard events?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You must implement key event handlers. These functions are called whenever a
key event is detected:

* :meth:`arcade.Window.on_key_press`
* :meth:`arcade.Window.on_key_release`

You need to implement your own versions of the above methods on your subclass
of :class:`arcade.Window`. The :ref:`arcade.key <key>` module contains
constants for specific keys.

For runnable examples, see the following:

* :ref:`sprite_move_keyboard`
* :ref:`sprite_move_keyboard_better`
* :ref:`sprite_move_keyboard_accel`

.. note:: If you are using :class:`Views <arcade.View>`, you can
          also implement key event handler methods on them.

.. _keyboard_modifiers:

Modifiers
---------

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
handlers <keyboard_event_handlers>`.

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
<keyboard_event_handlers>`.
