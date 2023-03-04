.. include:: <isonum.txt>

.. _menu_tutorial:


Making a Menu with Arcade's GUI
===============================

Step 1: Open a Window
---------------------

First, let's start a blank window with a view.

.. literalinclude:: menu_01.py
    :caption: Opening a Window
    :linenos:

Step 2: Switching to Menu View
-------------------------------

For this section we will switch the current view of the window to the menu view.


Imports
-------

First we will import the arcade gui:

.. literalinclude:: menu_02.py
    :caption: Importing arcade.gui
    :lines: 4-6
    :emphasize-lines: 5

Modify the MainView
-------------------

We are going to add a button to change the view. For drawing a button we would need a UIManager.

.. literalinclude:: menu_02.py
    :caption: Intialising the Manager
    :lines: 15-19
    :emphasize-lines: 18

After initialising the manager we need to enable it when the view is shown and disable it when the view is hiddien.

.. literalinclude:: menu_02.py
    :caption: Enabling the Manager
    :lines: 42-48
    :emphasize-lines: 46-47

.. literalinclude:: menu_02.py
    :caption: Disabling the Manager
    :lines: 37-39

We also need to draw the childrens of the menu in `on_draw`.

 .. literalinclude:: menu_02.py
    :caption: Drawing Children's of the Manager
    :lines: 49-56
    :emphasize-lines: 54-55

Now we have successfully setup the manager, only thing left it to add the button. We are using `UIAnchorLayout` to position the button.

  .. literalinclude:: menu_02.py
    :caption: Initialising the Button
    :lines: 20-36


Initialise the Menu View
------------------------

We make a boiler plate view just like we did in Step-1.

.. literalinclude:: menu_02.py
    :caption: Initialise the Menu View
    :lines: 57-70
