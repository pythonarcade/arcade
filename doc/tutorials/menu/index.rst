.. include:: <isonum.txt>

.. _menu_tutorial:


Making a Menu with Arcade's GUI
===============================

.. image:: menu.gif
    :width: 80%

This tutorial shows how to use most of arcade's gui's widgets.

Step 1: Open a Window
---------------------

.. image:: menu_01.png
    :width: 50%

First, let's start a blank window with a view.

.. literalinclude:: menu_01.py
    :caption: Opening a Window
    :linenos:

Step 2: Switching to Menu View
-------------------------------

.. image:: menu_02.png
    :width: 50%

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

We are going to add a button to change the view. For drawing a button we would need a ``UIManager``.

.. literalinclude:: menu_02.py
    :caption: Intialising the Manager
    :lines: 16-19
    :emphasize-lines: 4

After initialising the manager we need to enable it when the view is shown and disable it when the view is hiddien.

.. literalinclude:: menu_02.py
    :caption: Enabling the Manager
    :pyobject: MainView.on_show_view
    :emphasize-lines: 5-6

.. literalinclude:: menu_02.py
    :caption: Disabling the Manager
    :pyobject: MainView.on_hide_view

We also need to draw the childrens of the menu in ``on_draw``.

 .. literalinclude:: menu_02.py
    :caption: Drawing Children's of the Manager
    :pyobject: MainView.on_draw
    :emphasize-lines: 6-7

Now we have successfully setup the manager, only thing left it to add the button. We are using ``UIAnchorLayout`` to position the button. We also setup a function which is called when the button is clicked.

  .. literalinclude:: menu_02.py
    :caption: Initialising the Button
    :lines: 21-37

Initialise the Menu View
~~~~~~~~~~~~~~~~~~~~~~~~

We make a boiler plate view just like we did in Step-1 for switiching the view when the pause button is clicked.

.. literalinclude:: menu_02.py
    :caption: Initialise the Menu View
    :pyobject: MenuView

Program Listings
~~~~~~~~~~~~~~~~

* :ref:`menu_02` |larr| Where we are right now
* :ref:`menu_02_diff` |larr| What we changed to get here


Step 3: Setting Up the Menu View
--------------------------------

.. image:: menu_03.png
    :width: 50%

In this step we will setup the display buttons of the actual menu. The code written in this section is written for ``MenuView``

Initialising the Buttons
~~~~~~~~~~~~~~~~~~~~~~~~

First we setup buttons for resume, starting a new game, volume, options and exit.

.. literalinclude:: menu_03.py
    :caption: Initialising the Buttons
    :lines: 67-72

Displaying the Buttons in a Grid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After setting up the buttons we add them to ``UIGridLayout``, so that they can displayed in a grid like manner.

.. literalinclude:: menu_03.py
    :caption: Setting up the Grid
    :lines: 74-90

Final code for the ``__init__`` method after these.

.. literalinclude:: menu_03.py
    :caption: __init__
    :pyobject: MenuView.__init__

Program Listings
~~~~~~~~~~~~~~~~

* :ref:`menu_03` |larr| Where we are right now
* :ref:`menu_03_diff` |larr| What we changed to get here


Step 4: Configuring the Menu Buttons
------------------------------------

.. image:: menu_04.png
    :width: 50%

We basically add event listener for ``on_click`` for buttons.

Adding ``on_click`` Callback for Resume, Start New Game and Exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First we will add the event listener to resume, start_new_game and exit button as they don't have much to explain.

.. literalinclude:: menu_04.py
    :caption: Adding callback for button events 1
    :lines: 94-107

Adding ``on_click`` Callback for Volume and Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we need to implement an actual menu for volume and options, for that we have to make a class that acts like a window. Using ``UIMouseFilterMixin`` we catch all the events happening for the parent and respond nothing to them. Thus making it act like a window/view.

.. literalinclude:: menu_04.py
    :caption: Making a Fake Window.
    :pyobject: SubMenu

We have got ourselves a fake window currently. We now, pair it up with the volume and options button to trigger it when they are clicked.

.. literalinclude:: menu_04.py
    :caption: Adding callback for button events 2
    :lines: 109-123

Program Listings
~~~~~~~~~~~~~~~~

* :ref:`menu_04` |larr| Where we are right now
* :ref:`menu_04_diff` |larr| What we changed to get here

Step 5: Finalising the Fake Window aka the Sub Menu
---------------------------------------------------

.. image:: menu_05.png
    :width: 50%

We finalise the menu or you can call it the last step!

Editing the Parameters for the Sub Menu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We will edit the parameters for the sub menu to suit our needs. Will explain later why are those parameters needed.

.. literalinclude:: menu_05.py
    :caption: Editing parameters
    :lines: 153-156

We also need to change accordingly the places where we have used this class i.e options and volume ``on_click`` event listener. The layer parameter being set 1, means that this layer is always drawn on top i.e its the first layer.

.. literalinclude:: menu_05.py
    :caption: Editing arguments
    :lines: 109-131

Now you might be getting a little idea why we have edited the parameters but follow on to actually know the reason.


Adding a Title label
--------------------

We will be adding a ``UILabel`` that explains the menu. ``UISpace`` is a widget that can be used to add space around some widget, you can set its color to the background color so it appears invisible.

.. literalinclude:: menu_05.py
    :caption: Adding title label
    :lines: 179-181

Adding it to the widget layout.

.. literalinclude:: menu_05.py
    :caption: Adding title label to the layout
    :lines: 209-211


Adding a Input Field
~~~~~~~~~~~~~~~~~~~~~

We will use ``UIInputText`` to add an input field. The ``with_border()`` function creates a border around the widget with color(default argument is black) black and thickness(default argument is 2px) 2px. Add this just below the title label.

.. literalinclude:: menu_05.py
    :caption: Adding input field
    :lines: 183

Adding it to the widget layout.

.. literalinclude:: menu_05.py
    :caption: Adding input field to the layout
    :lines: 209-212
    :emphasize-lines: 4

If you paid attention when we defined the ``input_text`` variable we passed the ``text`` parameter with our ``input_text_default`` argument. We basically added those parameters in our sub menu so that it can be used by both volume and options button, with texts respecting their names. We will repeat this again in the last also for those of you who are skipping through this section :P.

Adding a Toggle Button
~~~~~~~~~~~~~~~~~~~~~~

Don't go on the section title much, in arcade the ``UITextureToggle`` is not really a button it switches between two textures when clicked. Yes, it functions like a button but by "is not really a button" we meant that it doesn't inherits the button class. We also pair it up horizontally with the toggle label.

.. literalinclude:: menu_05.py
    :caption: Adding toggle button
    :lines: 189-201

Adding it to the widget layout. Add this line after you have added the input field.

.. literalinclude:: menu_05.py
    :caption: Adding toggle button to the layout
    :lines: 213

Adding a Dropdowm
~~~~~~~~~~~~~~~~~

We add a dropdowm by using ``UIDropdown``.

.. literalinclude:: menu_05.py
    :caption: Adding dropdown
    :lines: 203-204

Adding it to the widget layout.

.. literalinclude:: menu_05.py
    :caption: Adding dropdown to the layout
    :lines: 214

Adding a Slider
~~~~~~~~~~~~~~~

The final widget. In arcade you can use ``UISlider`` to implement a slider. Theres a functionality to style the slider, this is also present for ``UIFlatButton`` and ``UITextureButton``.

.. literalinclude:: menu_05.py
    :caption: Adding slider
    :lines: 206-207

Adding it to the widget layout.

.. literalinclude:: menu_05.py
    :caption: Adding slider to the layout
    :lines: 215-216

Finishing touches
~~~~~~~~~~~~~~~~~

As we mentioned earlier, to explain the use of those parameters to the class. We basically used them so it can be used by both options and volume as we wanted to have different text for both.
For those who have read the full tutorial line-by-line; 'They will never know'. :D.
We also recommend to see the full code for this section.


Program Listings
~~~~~~~~~~~~~~~~

* :ref:`menu_05` |larr| Where we are right now
* :ref:`menu_05_diff` |larr| What we changed to get here
