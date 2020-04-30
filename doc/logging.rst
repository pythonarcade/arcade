.. _logging:

Logging
=======

You can get more information about what Arcade is doing by turning on logging.

Turn on logging
---------------

First, in your program import the
`logging library <https://docs.python.org/3/library/logging.html>`_:

.. code-block:: python

    import logging

Then turn add code to turn on logging. I suggest after the imports in your main
program file.

.. code-block:: python

    logging.basicConfig(level=logging.DEBUG)

This will cause the Arcade library to output some basic debugging information:

.. code-block:: text

    DEBUG:arcade.sprite_list:[352812080] Creating SpriteList use_spatial_hash=True is_static=False
    INFO:arcade.gl.context:Arcade version : 2.4a5
    INFO:arcade.gl.context:OpenGL version : 3.3
    INFO:arcade.gl.context:Vendor         : NVIDIA Corporation
    INFO:arcade.gl.context:Renderer       : GeForce GTX 980 Ti/PCIe/SSE2
    INFO:arcade.gl.context:Python         : 3.7.4 (tags/v3.7.4:e09359112e, Jul  8 2019, 19:29:22) [MSC v.1916 32 bit (Intel)]
    INFO:arcade.gl.context:Platform       : win32
    DEBUG:arcade.sprite_list:[352812080] _calculate_sprite_buffer: 0.012130399999999764 sec
    DEBUG:arcade.experimental.gui.ui_element:UIElement mouse over

Add More Info to Logs
---------------------

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

You can easily add logging to your own programs by defining a logger at the
top of your file:

.. code-block:: python

    LOG = logging.getLogger(__name__)

Then, any time you want to print, just use:

.. code-block:: python

    LOG.debug("This is my debug statement.")

