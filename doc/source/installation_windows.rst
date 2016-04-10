Installation on Windows
=======================

First you will need the address of your Arcade library in your computer. To find this, go to where you saved Arcade and open it in a file explorer window. 
At the top of the window will be the address bar, copy or memorize the address. 

To install Arcade, press the "windows key" + "R", this will open a window with a dialog box. Type "cmd" in the box and press enter or click the "OK" button. This will open your command line. 

At this point you will need to change to your Arcade directory. To do this type: cd (the address of arcade)
If you copied the address then after you type 'cd ' then right click the window and select paste. (Note: "ctrl" + "v" does not generally work for command line.

once you are in the correct directory, type 'make.bat'. You will know if it works if a lot of windows pop up on the screen.
Most errors that will be encountered during installation will occur here. If installation fails, you may need to install wheel.

================
Installing Wheel
================
To install wheel type 'pip install wheel'. If you encounter an error that says:
'pip" is not recognized as an internal or external command, operable program or batch file.
Then this means that Python was not added to your path. 
(This mean that your computer does not know to look at Python's Scripts folder to find the 'pip' command)

===========================
Add Python Scripts to Path
===========================
To add Python to the path, you will first need to find your Python folder. If it was installed in the default location, then look in your C: drive in explorer. 
when you find your version of Python, open it and find the Scripts folder inside. When you get to the Scripts folder, copy the address in the address bar.

To customize path, right click the bottom right-hand corner of your screen and select the System option.
In the System window there is an option for advanced system settings, open it.
In the System Properties window you should be in the 'Advanced' tab. There should also be a button that says "Environment Variables" that you will need to open.
The Path variable will be in a list of system variables. Find it and select Edit when you have Path highlighted.
Go to the end of the text in the Variable value dialog box. Type a ';' at the end and then paste the address of your Scripts folder.
Select OK on the menus and exit out of your System window. Because you changed the path, you will need to close command line and re-open it again. 

================================
After Adding Scripts to Path
================================
Return to the directory where your Arcade is and type "make.bat" again.	if more things happen in the console than before, but you are still not seeing the group of windows that pop up, search though the information that got written into the console. If you can find an error message like the one before saying that "Python is not recognized as an internal command", then you will need to add Python to the path as well. Follow the same instructions from the "add Python Scripts to path" but with the address for the python folder itself.