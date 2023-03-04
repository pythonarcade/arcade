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
    :lines: 4-5
    :emphasize-lines: 2

Modify the MainView
-------------------

We are going to add a button to change the view. For drawing a button we would need a UIManager.

.. literalinclude:: menu_02.py
    :caption: Intialising the Manager
    :lines: 15-18
    :emphasize-lines: 4

After initialising the manager we need to enable it when the view is shown and disable it when the view is hiddien.

.. literalinclude:: menu_02.py
    :caption: Enabling the Manager
    :pyobject: MainView.on_show_view
    :emphasize-lines: 3-4

.. literalinclude:: menu_02.py
    :caption: Disabling the Manager
    :pyobject: MainView.on_hide_view

We also need to draw the childrens of the menu in `on_draw`.

 .. literalinclude:: menu_02.py
    :caption: Drawing Children's of the Manager
    :pyobject: MainView.on_draw
    :emphasize-lines: 6-7

Now we have successfully setup the manager, only thing left it to add the button. We are using `UIAnchorLayout` to position the button.

  .. literalinclude:: menu_02.py
    :caption: Initialising the Button
    :lines: 20-35


Initialise the Menu View
------------------------

We make a boiler plate view just like we did in Step-1.

.. literalinclude:: menu_02.py
    :caption: Initialise the Menu View
    :pyobject: MenuView

Step 3: Setting Up the Menu View
--------------------------------

In this step we will setup the display buttons of the actual menu.

Initialising the Buttons
------------------------

First we setup buttons for resume, starting a new game, volume, options and exit.

.. literalinclude:: menu_03.py
    :caption: Initialising the Buttons
    :lines: 63-68

Displaying the Buttons in a Grid
---------------------------------

After setting up the buttons we add them to `UIGridLayout`, so that they can displayed in a grid like manner.

.. literalinclude:: menu_03.py
    :caption: Setting up the Grid
    :lines: 70-86

Final code for the `__init__` method after these.

.. literalinclude:: menu_03.py
    :caption: __init__
    :pyobject: MenuView.__init__
