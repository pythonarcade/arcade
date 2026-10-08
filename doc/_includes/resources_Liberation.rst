.. figure:: images/fonts_liberation.png
   :alt: The bundled Liberation font family trio.
   :align: center

.. Put the text *after* the CSS, or add <br> via .. raw:: html blocks
.. since the CSS may be broken.

Arcade also includes the Liberation font family. This trio is designed and
licensed specifically to be a portable, drop-in set of substitutes for Times, Arial,
and Courier fonts. It uses the proven, commercial-friendly `SIL Open Font License`_.

Liberation Sans is Arcade's default font. Each family is loaded the first
time you use it, so you can use ``font_name="Liberation Mono"`` without
loading anything. To load them ahead of time, for example during a loading
screen, use :py:func:`arcade.resources.load_liberation_fonts`.
