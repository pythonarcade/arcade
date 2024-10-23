.. _how-to-get-help:

How to Get Help
===============

The best places to get help are the help channels on the `Arcade Discord`_ server.
They are located in the 3rd category from the top in the channel list:

.. figure:: /images/community/how_to_get_help/discord_help_channels.png
    :scale: 50%
    :alt: A screenshot of the Discord server's channel categories with
          an arrow pointing to the help channels.


To get help, start by choosing an inactive help channel. Inactive means
that the last message was sent a day or more ago. If all the help
channels have been active in that time, choose the one in with the
earliest last message.

Once you have chosen a channel, do your best to provide the following
information:

#. A very short explanation of what you're trying to do
#. The problem you're having, with any
   :ref:`error output formatted properly <help-sharing-with-markdown-terminal>`
#. Your code, with
   :ref:`proper formatting <help-sharing-with-markdown-python>`
#. Which :ref:`version of Arcade <help-basic-environment-info>` you're
   using and how you installed it

Here's an example as a series of Discord messages (click or tap to
enlarge):

.. figure:: /images/community/how_to_get_help/discord_help_example.png
    :scale: 75%
    :alt: An example of a good series of messages requesting help,
          including all the point above.

The rest of this page will explain how to format your messages like the
example above.

.. _help-sharing-code:

Sharing & Formatting Your Code
------------------------------

Other people need to be able to see your code to help you. There are two
preferred ways of showing it to them:

#. :ref:`Pasting into Discord <help-sharing-with-markdown-python>` for
   small amounts of code
#. :ref:`Using a code hosting service <help-sharing-with-code-hosting>`
   for 1 or more files

.. _help-sharing-with-markdown:

Formatting for Discord & Github Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is important to format code and terminal output when posting it.
Formatting helps other people understand what you've pasted.

Both Discord & GitHub issues use the same 3 steps below.

Step 1 : Find your Backtick Key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The \` characters below are not single quotes or apostrophes. They're
called backticks.

On standard US keyboards, the backtick key is the same one used to type
a tilda (`~`). You can find it to the left of the 1 key.

For other keyboard layouts, please
`see this StackExchange answer <https://superuser.com/a/254077>`_.

Step 2: Format & Paste
^^^^^^^^^^^^^^^^^^^^^^

Formatting Python code is nearly identical to formatting terminal output.

.. _help-sharing-with-markdown-python:

Formatting Code
"""""""""""""""

Once you have found your backtick key, you can format your code like
this:

.. code-block:: markdown

    ```python
    # paste your code between the top and bottom lines!
    print("Do stuff!")
    ```

If you cannot type a backtick on your keyboard, you can copy the example
above to your clipboard. For convenience, clicking the icon at the top
right of the example box will copy it for you. You can paste it into
Discord's message box as shown below:

.. figure:: /images/community/how_to_get_help/discord_code_entry_desktop.png
    :alt: The example code block from above pasted into Discord's
          message entry field.

.. _help-sharing-with-markdown-terminal:

Formatting Terminal Output
""""""""""""""""""""""""""

Terminal output, such as error traceback, can be formatted in almost the
exact same way. The difference is that you don't type ``python`` after
the three backticks on the first line:

.. code-block:: markdown

    ```
    Traceback (most recent call last):
      File "/home/user/src/arcade/helpexample.py", line 34, in <module>
        main()
      File "/home/user/src/arcade/helpexample.py", line 29, in main
        window.setup()
      File "/home/user/src/arcade/helpexample.py", line 17, in setup
        self.player_sprite = arcade.Sprite(img, 1.0)
      File "/home/user/src/arcade/arcade/sprite.py", line 243, in __init__
        self._texture = load_texture(
      File "/home/user/src/arcade/arcade/texture.py", line 543, in load_texture
        file_name = resolve(file_name)
      File "/home/user/src/arcade/arcade/resources/__init__.py", line 40, in resolve
        raise FileNotFoundError(f"Cannot locate resource : {path}")
    FileNotFoundError: Cannot locate resource : my_player_image.png
    ```

Step 3: Post it!
^^^^^^^^^^^^^^^^

On Discord, you can now press enter to send your message like any
other formatted text.

For reporting bugs on GitHub, the same general formatting principles
apply, but with a few differences.

You will also have to click Submit new issue instead of pressing enter.
Please see the following links for more information on reporting bugs,
GitHub issues, and their supported markdown syntax:

* `How to Report Bugs Effectively <https://www.chiark.greenend.org.uk/~sgtatham/bugs.html>`_
* `GitHub issue creation documentation <https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue>`_
* `GitHub general markdown guide <https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax>`_
* `GitHub's code formatting documentation <https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-and-highlighting-code-blocks#syntax-highlighting>`_


.. _help-sharing-with-code-hosting:

Code Hosting
~~~~~~~~~~~~

Code hosting services provide a formatted web view of your code which
you can share with a link.

To share code snippets or single files without a signup, you can use
`the code pasting service <https://paste.pythondiscord.com/>`_
provided by the `Python Discord <https://www.pythondiscord.com/>`_.
If you're ok with signing up for something, there are also
`GitHub Gists <https://docs.github.com/en/get-started/writing-on-github/editing-and-sharing-content-with-gists/creating-gists>`_.
Afterwards, you can paste a link in Discord or another chat application.

A more advanced way to share code is to use a git hosting service. It
takes effort to learn how to use git, but it has many benefits. Some of them
include:

* Easy backup & undo
* Easier collaboration with others
* Allow people to view your entire project's source to help you better

Popular Git hosting options include:

* `GitHub <https://github.com>`_
* `GitLab <https://gitlab.com>`_

.. _help-basic-environment-info:

Arcade Version & Basic Environment Info
---------------------------------------

This section assumes you have
:ref:`installed arcade <install>` and activated your
virtual environment.

To get basic information about your current Arcade version and
environment, run this from within your development environment:

.. code-block:: console

    arcade

The command is cross-platform, which means it should work the same way
regardless of whether you're on Mac, Linux, or Windows.

The output should should look something like this:

.. code-block::

    Arcade 2.7.0
    ------------
    vendor: Intel
    renderer: Mesa Intel(R) UHD Graphics 620 (KBL GT2)
    version: (4, 6)
    python: 3.9.2 (default, Feb 28 2021, 17:03:44)
    [GCC 10.2.1 20210110]
    platform: linux


It's ok if the output looks different from the example above. The second
half of each line may change to reflect your Arcade version, hardware,
and operating system.

You can copy and paste the output into Discord or GitHub using the
`markdown formatting for terminal output <help-sharing-code-with-markdown-terminal>`_
described earlier.

Output like the example below means that something is wrong:

.. code-block:: console

    bash: arcade: command not found

You should still `include the output <help-sharing-with-markdown-terminal>`_
as part of a request for help.

If you want to try fixing the problem yourself before getting help,
the likeliest explanations for the error message above are:

* Forgetting to activate your virtual environment
* Not :ref:`installing Arcade <install>` successfully
