:orphan:

.. _sprite_move_keyboard_better:

Better Move By Keyboard
=======================

.. image:: sprite_move_keyboard.png
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
    :emphasize-lines: 65-69, 100-111, 113-116, 121-128, 133-140
