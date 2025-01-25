.. figure:: images/fonts_liberation.png
   :alt: The bundled Liberation font family trio.
   :align: center

.. Put the text *after* the CSS, or add <br> via .. raw:: html blocks
.. since the CSS may be broken.

Arcade also includes the Liberation font family. This trio is designed and
licensed specifically to be a portable, drop-in set of substitutes for Times, Arial,
and Courier fonts. It uses the proven, commercial-friendly `SIL Open Font License`_.

To use these fonts, you may use either approach:

* load files for specific variants via :py:func:`arcade.load_font`
* load all variants at once with :py:func:`arcade.resources.load_liberation_fonts`.
