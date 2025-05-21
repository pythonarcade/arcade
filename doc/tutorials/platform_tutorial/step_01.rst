
.. _platformer_part_one:

Step 1 - Install and Open a Window
----------------------------------

You will do two things in this section.

1) Run the code from the arcade module directly. This will open a simple window.

2) Create your own file with the copied code to work on for the rest of the tutorial.
   Run it, you will get the same window, but THIS copy you control!

Installation
~~~~~~~~~~~~
For any of this to work, you need Python with the Arcade module installed.

* Setup instruction are here: :ref:`install`.

Verify the Installation (Step 1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following code from a terminal in the folder that contains the arcade directory.

.. code-block::

  python -m arcade.examples.platform_tutorial.01_open_window

You should end up with a window like this:

.. image:: step_01.png
   :width: 75%

The window is pretty useless... You can minimize it and even close it! However, if you got
this going, you have succeeded in what is generally the hardest part of any new project
- getting the environment setup! Congratulations! (Commence party dance sequence!)

.. note::

  This is a fixed-size window. It is possible to have  a
  :ref:`resizable_window` or a :ref:`full_screen_example`, but there are more
  interesting things we can do first. Therefore we'll stick with a fixed-size
  window for this tutorial.


Coding...The fun part! (Step 2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You also need a code editor. There are dozens of options and we can't keep up with them
here. A simple text editor could work, but better options abound. A web search is your
friend - search for "Python editor" and pick one that looks good. Visual Studio Code
(VS Code) is a nice free option. PyCharm is another.


* Open your editor of choice and make a new file, call it main.py (the name is important!)
* Copy this code into it.

.. literalinclude:: ../../../arcade/examples/platform_tutorial/01_open_window.py
    :caption: 01_open_window.py - Open a Window
    :linenos:

* Run the code from the same environment and in the folder with the code:

.. code-block::

  python main.py

What is this code?
~~~~~~~~~~~~~~~~~~

Explaining in depth every part of the code would be tedious and pretty overwhelming,
and ultimatly not the most useful way to learn. But knowing the intent of sections is good!

Comments
    Triple quotations mark the begin and end of comments - sections of
    code that the computer ignores. It is for us humans!
    A second way of making a comment is the '#' symbol which lets python know to
    ignore everything on that line after the symbol.

import arcade
    This tells python which tools it needs to use to run the code. The magic sauce that does
    all the heavy lifting for the program so that you can focus on being creative!

# Constants section
    Remember how we said the window is a fixed size? Can you guess WHAT size it is fixed to
    from these lines? Did you notice a title on the window (go ahead and peek!).

class GameView(arcade.Window):
    Classes are extremely important programming concepts. In simple terms, it is a collection
    of data that you do things with. It keeps things organized!

def __init__(self):
    Data sets that make up class objects need initial information. You provide that here.

def setup(self):
    pass? what are we passing? Well, nothing, this is a place holder for future awesome code.
    pass tells Python that the function does nothing at the moment and it can move along.

def on_draw(self):
    Right now this function runs a simple command - self.clear(). Notice all the comments! That
    is so that you (the coder) knows what is going on in the function. More on this section to follow!

def main():
    This is the entry point for Python. When you run a program, Python looks for a main() function
    and runs it. Then three steps happen:

1) window = GameView() -> Your window object is created. Your __init__ function is automatically called.
2)  window.setup() - > You run the window object's setup function... Which does nothing at the moment (pass!)
3) arcade.run() -> You turn on the engine and see the results. The program stays here until the
   window is closed. Then with nothing else to do, the program will terminate.

if __name__ == "__main__":
    If Python was run by starting this file in particular, then its "__name__" value will be "__main__".
    And the main() function will be called. Remember how we said the name of the file was important?

Challenge Exercises
~~~~~~~~~~~~~~~~~~~

Once you get the code working, try figuring out how to adjust the code so you can:

* Change the screen size(or even make the Window resizable or fullscreen)
* Change the title
* Change the background color

  * See the documentation for :ref:`color`
  * See the documentation for :ref:`csscolor`

* Look through the documentation for the :class:`arcade.Window`
  class to get an idea of everything it can do.
* Break it! Yes this sounds bad, but comment out some sections of the code and try to run it.
  You will make mistakes and this can help you get familure with error messages. Also, see if
  you can see in the error message WHERE the problem exists or other such clues. You already
  know because you made them... Make sure you save the good code and it is functional again
  before moving on.
