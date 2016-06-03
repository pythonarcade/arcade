Installation on the Mac
=======================

1. Go to the `Python website 
   <https://www.python.org/downloads/release/python-351/>`_ and download the
   "Mac OS X 64-bit / 32-bit installer".  Find the file in your Download folder
   and double-click it to install

2. All (most?) computers have a terminal window where a user can type commands 
   and interact directly with the computer, without any windows or GUI 
   applications popping up.  To start the terminal, open Spotlight 
   (Command + Space) and type "Terminal" (without the quotes), then press 
   enter.

3. Install virtualenv.  This allows you to install Python packages without
   affecting the system-wide Python installation.  Run the following command
   in your terminal.

``sudo pip3 install virtualenv``

4. Use virtualenv to create a virtual environment specifically for your project
   by running the following command in your terminal.

``virtualenv ~/.virtualenvs/arcade``

5. Activate the virtualenv you just created.  (You may need to do this each
   time you open a new terminal window.  It is possible to make the terminal do
   this for you each time you open a new window, but that is beyond the scope
   of these instructions.)

``source ~/.virtualenvs/arcade/bin/activate``

6. Install the Python Arcade Library, by running the following command

``pip install arcade``

7. Download the community edition of PyCharm for the Mac from the `Jetbrains
   website <https://www.jetbrains.com/pycharm/download/>`_. Double click on the
   file you downloaded to install it.

8. Create a new project in PyCharm. Because the Mac often has multiple versions
   of Python installed on it, when creating a project make sure to select 
   version 3.5.

.. image:: images/pycharm_mac_select_python.png
