
Vertical Synchronization
========================

What is vertical sync?
----------------------

Vertical synchronization (vsync) is a window option in which the
video card is prevented from doing anything visible to the display
memory until after the monitor finishes its current refresh cycle.

To enable vsync in arcade::

    # On window creation
    arcade.Window(800, 600, "Window Title", vsync=True)

    # While the application is running
    window.set_vsync(True)

This have advantages and disadvantages depending on the situation.

Most windows are what we call "double buffered". This means
the window actually has two surfaces. A visible surface and a 
hidden surface. All drawing commands will end up in the
hidden surface. When we're done drawing our frame the hidden
and visible surfaces swap places and the new frame is revealed
to the user.

If this "dance" of swapping surfaces is not timed correctly 
with your monitor you might experience small hiccups in movement.

Vertical sync disabled as a default
------------------------------------

The arcade window is by default created with vertical sync
disabled. This is a much safer default for
a number of reasons.

* In some environments vertical sync is capped to 30 fps.
  This can make the game run at half the speed if ``delta_time``
  is not accounted for. We don't expect beginners take
  ``delta_time`` into consideration in their projects.
* If threads are used all threads will stall while the
  application is waiting for vertical sync

We cannot guarantee that vertical sync is disabled if
this is enforced on driver level. The vast amount of
driver defaults lets the application control this.

Advantages of vertical sync
---------------------------

If you have any kind of movement, scrolling or animation
in your application you might have noticed a very subtle 
hiccup periodically or randomly. This can be reduced or
entirely removed by enabling vertical sync. In some
environments/platforms you can even experience
`screen tearing <https://en.wikipedia.org/wiki/Screen_tearing>`_.

When vsync is enabled we have to make sure all movement
is takes ``delta_time`` into consideration. **This can also
improve smoothness when vsync is not enabled**::

    # Move 100 units in one second
    MOVEMENT_SPEED = 100

    def on_update(self, delta_time):
        # Move your sprite based on the time since the last frame.
        # This will make the sprite move along the x axis by
        # 100 units in one second
        self.sprite.center_x += MOVEMENT_SPEED * delta_time
