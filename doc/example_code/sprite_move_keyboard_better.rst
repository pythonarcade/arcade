:orphan:

.. _sprite_move_keyboard_better:

Better Move By Keyboard
=======================

.. image:: images/sprite_move_keyboard.png
    :width: 600px
    :align: center
    :alt: Screen shot of moving a sprite by keyboard

If a player presses the left key, the sprite should move left. If the player
hits both left and right, the player should stop. If the player lets off the left
key, keeping the right key down, the player should move right.

The simpler method of handling keystrokes will not handle this correctly. This
code tracks which key is down or up, and handles it properly.

See the highlighted sections.

.. literalinclude:: ../../arcade/examples/sprite_move_keyboard_better.py
    :caption: sprite_move_keyboard_better.py
    :linenos:
    :emphasize-lines: 65-69, 96-109, 119-133, 135-149
