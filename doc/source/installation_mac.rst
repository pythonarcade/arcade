Installation on the Mac
=======================

==============
Finding Arcade
==============
Go to where you saved Arcade on your computer and open it in a window and select any random file in the folder.
At the top of the window, click on the gear and select the 'Get Info' option.
In the new window that opened, in the section called 'General Settings', you will find a 'Where:' section.
Copy the location.

============================================
Getting to Terminal and the Arcade Directory
============================================
To open terminal press the 'command' key + the space bar, and type 'terminal'.

In the terminal, you will need to change to the Arcade directory.
To do this, type "cd " and paste Arcade's address into the terminal after the space after 'cd' and then press enter.

============================
Installing Arcade (Best Case)
============================
To install Arcade, type "cat make.bat" into the terminal.

If the installation was successful, then you will see a lot of things happening in the terminal and there will be several windows, briefly, popping up on the screen.

If nothing really happens, then you may need to do a more manual installation.

===================
Manual Installation (In Progress)
===================
Python3 setup.py clean
Python3 setup.py build
pip3 install wheel sphinx pyglet pillow PyOpenGl Coveralls mock numpy
sphinx-build -b html doc/source doc/build/html
coverage run --source arcade setup.py test


