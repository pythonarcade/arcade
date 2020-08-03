Working with the Keyboard
=========================

.. _keyboard_modifiers:

Modifiers
---------

The modifiers that are held down when the event is generated are combined in a
bitwise fashion and provided in the modifiers parameter. The modifier constants
defined in arcade.key are:

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

For example, to test if the shift key is held down:

.. code-block:: python

    if modifiers & MOD_SHIFT:
        pass

Unlike the corresponding key symbols, it is not possible to determine whether
the left or right modifier is held down (though you could emulate this behavior
by keeping track of the key states yourself).
