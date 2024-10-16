.. _uicolor:

arcade.uicolor package
======================

.. _FlatUI: https://materialui.co/flatuicolors/

This module contains colors from MaterialUI's `FlatUI`_ palette.

.. note:: `WHITE` and `BLACK` are aliases.

           These are imported from `arcade.color`.

You can specify colors four ways:

* Standard CSS color names :ref:`csscolor`: ``arcade.csscolor.RED``
* Nonstandard color names (this package): ``arcade.color.RED``
* Three-byte numbers: ``(255, 0, 0)``
* Four-byte numbers (fourth byte is transparency. 0 transparent, 255 opaque): ``(255, 0, 0, 255)``
