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
~~~~~~~

First we will import the arcade gui:

.. literalinclude:: menu_02.py
    :caption: Importing arcade.gui
    :lines: 4-5
    :emphasize-lines: 2

Modify the MainView
~~~~~~~~~~~~~~~~~~~~

We are going to add a button to change the view. For drawing a button we would need a UIManager.

.. literalinclude:: menu_02.py
    :caption: Intialising the Manager
    :lines: 15-18
    :emphasize-lines: 4

After initialising the manager we need to enable it when the view is shown and disable it when the view is hiddien.

.. literalinclude:: menu_02.py
    :caption: Enabling the Manager
    :pyobject: MainView.on_show_view
    :emphasize-lines: 5-6

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
    :lines: 20-36

Initialise the Menu View
~~~~~~~~~~~~~~~~~~~~~~~~

We make a boiler plate view just like we did in Step-1.

.. literalinclude:: menu_02.py
    :caption: Initialise the Menu View
    :pyobject: MenuView

Program Listings
~~~~~~~~~~~~~~~~

* :ref:`menu_02` |larr| Where we are right now
* :ref:`menu_02_diff` |larr| What we changed to get here


Step 3: Setting Up the Menu View
--------------------------------

In this step we will setup the display buttons of the actual menu.

Initialising the Buttons
~~~~~~~~~~~~~~~~~~~~~~~~

First we setup buttons for resume, starting a new game, volume, options and exit.

.. literalinclude:: menu_03.py
    :caption: Initialising the Buttons
    :lines: 64-69

Displaying the Buttons in a Grid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After setting up the buttons we add them to `UIGridLayout`, so that they can displayed in a grid like manner.

.. literalinclude:: menu_03.py
    :caption: Setting up the Grid
    :lines: 71-87

Final code for the `__init__` method after these.

.. literalinclude:: menu_03.py
    :caption: __init__
    :pyobject: MenuView.__init__

Program Listings
~~~~~~~~~~~~~~~~

* :ref:`menu_03` |larr| Where we are right now
* :ref:`menu_03_diff` |larr| What we changed to get here


Step 4: Configuring the Menu Buttons
------------------------------------

We basically add event listener for `on_click` for buttons.

Adding `on_click` Callback for Resume, Start New Game and Exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First we will add the event listener to resume, start_new_game and exit button as they don't have much to explain.

.. literalinclude:: menu_04.py
    :caption: Adding callback for button events 1
    :lines: 91-104

Adding `on_click` Callback for Volume and Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we need to implement an actual menu for volume and options, for that we have to make a class that acts like a window. Using `UIMouseFilterMixin` we catch all the events happening for the parent and respond nothing to them. Thus making it act like a window/view.

.. literalinclude:: menu_04.py
    :caption: Making a Fake Window.
    :pyobject: SubMenu

We have got ourselves a fake window currently. We now, pair it up with the volume and options button to trigger it when they are clicked.

.. literalinclude:: menu_04.py
    :caption: Adding callback for button events 2
    :lines: 106-114

Program Listings
----------------

* :ref:`menu_04` |larr| Where we are right now
* :ref:`menu_04_diff` |larr| What we changed to get here
