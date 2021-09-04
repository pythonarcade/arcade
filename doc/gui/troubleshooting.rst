
.. _gui_troubleshooting:

Troubleshooting & Hints
^^^^^^^^^^^^^^^^^^^^^^^

:class:`UILabel` does not show the text after it was updated
............................................................

Currently the size of :class:`UILabel` is not updated after modifying the text.
Due to the missing information, if the size was set by the user before, this behaviour is intended for now.
To adjust the size to fit the text you can use :meth:`UILabel.fit_content`.

In the future this might be fixed.
