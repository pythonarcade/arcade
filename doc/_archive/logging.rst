.. _logging:

Logging
=======

Arcade has a few options to log additional information around timings and how
things are working internally. The two major ways to do this by turning on
logging, and by querying the OpenGL context.

Turn on logging
---------------

The quickest way to turn on logging is to add this to the start of your main
program file:

.. code-block:: python

    arcade.configure_logging()

This will cause the Arcade library to output some basic debugging information:

.. code-block:: text

    2409.0003967285156 arcade.sprite_list DEBUG - [386411600] Creating SpriteList use_spatial_hash=True capacity=100
    2413.9978885650635 arcade.gl.context INFO - Arcade version : 2.4a5
    2413.9978885650635 arcade.gl.context INFO - OpenGL version : 3.3
    2413.9978885650635 arcade.gl.context INFO - Vendor         : NVIDIA Corporation
    2413.9978885650635 arcade.gl.context INFO - Renderer       : GeForce GTX 980 Ti/PCIe/SSE2
    2413.9978885650635 arcade.gl.context INFO - Python         : 3.7.4 (tags/v3.7.4:e09359112e, Jul  8 2019, 19:29:22) [MSC v.1916 32 bit (Intel)]
    2413.9978885650635 arcade.gl.context INFO - Platform       : win32
    3193.9964294433594 arcade.sprite_list DEBUG - [386411600] _calculate_sprite_buffer: 0.013532099999999936 sec

Custom Log Configurations
~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to add your own logging, or change the information printed in the
log, you can do it with just a bit more code.

First, in your program import the
`logging library <https://docs.python.org/3/library/logging.html>`_:

.. code-block:: python

    import logging

The code to turn on logging looks like this:

.. code-block:: python

    logging.basicConfig(level=logging.DEBUG)

You can get even more information by using a formatter to add time, file name,
and even line number information to your output:

.. code-block:: python

    format = '%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s()] %(message)s'
    logging.basicConfig(format=format,
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

...which changes the output to look like:

.. code-block:: text

    13:40:50,226 DEBUG    [sprite_list.py:720 _calculate_sprite_buffer()] [365177904] _calculate_sprite_buffer: 0.00849660000000041 sec
    13:40:50,398 DEBUG    [ui_element.py:58 on_mouse_over()] UIElement mouse over

You can add logging to your own programs by putting one of these lines
at the top of your program:

.. code-block:: python

    # Get your own logger
    LOG = logging.getLogger(__name__)
    # or get Arcade's logger
    LOG = logging.getLogger('arcade')

Then, any time you want to print, just use:

.. code-block:: python

    LOG.debug("This is my debug statement.")

Getting OpenGL Stats Using Query Objects
----------------------------------------

If you'd like more information on the time it takes to draw, you can query
the OpenGL context ``arcade.Window.ctx`` as this example shows:

.. code-block:: python

    def on_draw(self):
        """ Render the screen. """
        self.clear()

        query = self.ctx.query()
        with query:
            # Put the drawing commands you want to get info on here:
            self.my_sprite_list.draw()

        print()
        print(f"Time elapsed       : {query.time_elapsed:,} ns")
        print(f"Samples passed     : {query.samples_passed:,}")
        print(f"Primitives created : {query.primitives_generated:,}")

The output from this looks like the following:

.. code-block:: text

    Time elapsed       : 7,136 ns
    Samples passed     : 390,142
    Primitives created : 232
