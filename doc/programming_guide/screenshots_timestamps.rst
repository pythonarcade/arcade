.. _debug-helpers:

Screenshots & Timestamps
========================

Sometimes, you need to export data to separate files
instead of :ref:`logging with lines of text.<logging>`.

Arcade has a limited set of convenience functions to help you save
screenshots and other data this way.

Keep the following in mind:

* These convenience functions are mostly for debugging
* They are built for flexibility and ease of use
* They are not optimized performance, especially video
* Arcade's timestamp helper is a fallback for when you can't use
  :ref:`much better third-party options <debug-better-datetime>`

To learn about better tools for screen recording, please see
:ref:`debug-screenshot-i-need-video`.


.. _debug-screenshots:

Screenshots
-----------

Arcade's screenshot helpers do one of three things:

* Save to a file path
* Return a :py:class:`PIL.Image`
* Query pixels at coordinates

All of them have simliar :ref:`limitations <debug-screenshot-limitations>`
due to how they copy data.

Saving Screenshots to Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The most convenient ones are often the ones which save to disk
immediately:

* :py:meth:`Window.save_screenshot <arcade.Window.save_screenshot>`
* :py:func:`arcade.save_screenshot`

All of them have the same API and behavior. Since Arcade assumes
you will only have one window, :py:func:`arcade.save_screenshot`
is an easy-access wrapper around the other.

You can also get a raw :py:class:`PIL.Image` object by using the
following functions:


.. _debug-screenshots-howto:

Screenshot Saving Example
"""""""""""""""""""""""""

The following code saves a screenshot to a file:

.. literalinclude:: ../../arcade/examples/debug_screenshot.py
   :caption: How to take a debug screenshot.

Since it randomizes the circles, the result will be similar yet not
identical to the output below.

.. image:: ../example_code/how_to_examples/debug_screenshot.png
   :width: 800px
   :align: center
   :alt: Screen shot produced by the screenshot method.

.. _debug-screenhots-pil-image:

Getting PIL Images
^^^^^^^^^^^^^^^^^^

You can also get a :py:class:`PIL.Image` object back if you need
finer control.

.. _dbug-screenshots-pixels:

Pixel Queries
^^^^^^^^^^^^^

It's possible to query pixels directly.

However, this is best reserved for tests since it may have performance
costs.


.. _debug-screenshot-limitations:

Screenshot Limitations
^^^^^^^^^^^^^^^^^^^^^^

Arcade's screenshot helpers are not intended for rendering real-time
video. They will probably be too slow for many reasons, including:

* Copying data from the GPU back to a computer's main memory
* Using the CPU to run :py:meth:`Image.save <PIL.Image.save>` instead
  of the GPU
* Systems with slow drives or heavy disk usage may get stuck waiting
  to save individual files


.. _debug-screenshot-i-need-video:

I Need to Save Video!
^^^^^^^^^^^^^^^^^^^^^

Sometimess, it's easier to :ref:`get help <how-to-get-help>` if you
record a bug on video.

The cheapest and most reliable tools have tradeoffs:

*  Pre-installed video records are often easy to use but limmited
* `OBS <https://obsproject.com/>`_ is powerful but complicated

For :ref:`getting help <how-to-get-help>`, the first set of tools
is often best.

There are ways of recording video with Python, but they have variable
quality. Very advanced users may be able to get `ffmpeg <https://ffmpeg.org/>`_
or other libraries to work. However, these can come with risks or costs:

* Your project must be able to use (L)GPL-licensed code
* It may be difficult to implement or get adequate performance
* The binaries can be very large

Like OBS, ffmpeg is powerful and complicated. To learn more, see
:external+pyglet:ref:`pyglet's ffmpeg overview <guide-supportedmedia-ffmpeg>`
in their programming guide. Note that pyglet might only support reading media
files. Wrting may require additional dependencies or non-trivial work.

.. _debug-timestamps:

Filename Timestamps
-------------------

In addition to Arcade's :ref:`logging` features,
:py:func:`arcade.get_timestamp` is a minimal helper for
generating timestamped filenames.

Calling it without arguments returns a string which specifies the
current time down six places of microseconds.

.. code-block:: python

   # This output happens at exactly 3PM on April 3rd, 2024 in local time
   >>> arcade.get_timestamp()
   '2024_04_02_1500_00_000000'

.. _debug-timestamps-who:

Who Is This For?
^^^^^^^^^^^^^^^^

Everyone who can't use :ref:`a better alternative <debug-better-datetime>`:

* Students required to use only Arcade and Python builtins
* Anyone who needs to minimize install size
* Game jam participants with a deadline

In each of these cases, :py:func:`~arcade.get_timestamp` can help
write cleaner data export code a little faster.

.. code-block:: python

   # This example dumps character data to a file with a timestamped name.
   import json
   from pathlib import Path
   from typing import Dict, Any
   from arcade import get_timestamp

   BASE_DIR = Path("debug")

   def log_game_character(char: Dict[str, Any]) -> None:

       # Decide on a filename
       filename = f"{char['name']}{get_timestamp()}.json"
       character_path = BASE_DIR / filename

       # Write the data
       with character_path.open("w") as out:
           json.dump(char, out)


   # Set up our data
   parrot = dict(name='parrot', funny=True, alive=False)

   # Write it to a timestamped file
   log_game_character(parrot)

.. _debug-timestamps-custom:

Customizing Output
^^^^^^^^^^^^^^^^^^

Argument Overview
"""""""""""""""""

The ``when``, ``how``, and ``tzinfo`` keyword arguments allow using
:ref:`compatible <strftime-strptime-behavior>` objects and format
strings:

.. list-table::
   :header-rows: 1

   * - Keyword Argument
     - What it Takes
     - Default

   * - ``when``
     - ``None`` or anything with a :ref:`datetime-like <strftime-strptime-behavior>`
       ``strftime`` method
     - Calling
       :py:meth:`datetime.now(tzinfo) <datetime.datetime.now>`

   * - ``how``
     - A :ref:`C89-stlye date format string <strftime-strptime-behavior>`
     - ``"%Y_%m_%d_%H%M_%S_%f%Z"``

   * - ``tzinfo``
     - ``None`` or a valid :py:class:`datetime.tzinfo` instance
     - ``None``


.. _debug-timestamps-example-when-how:

Example of Custom When and How
""""""""""""""""""""""""""""""

.. code-block:: python

   >>> from datetime import date
   >>> DAY_MONTH_YEAR = '%d-%m-%Y'
   >>> today = date.today()
   >>> today
   datetime.date(2024, 4, 3)
   >>> arcade.get_timestamp(when=today, how=DAY_MONTH_YEAR)
   '03-04-2024'


.. _debug-timestamps-example-timezone:

Example of Custom Time Zones
""""""""""""""""""""""""""""

.. _UTC_Wiki: https://en.wikipedia.org/wiki/Coordinated_Universal_Time

Using `UTC <UTC_Wiki>`_ is a common way to reduce confusion about when
something happened. On Python 3.8, you can use
:py:class:`datetime.timezone`'s ``utc`` constant with this function:

.. code-block:: python

   >>> from datetime import timezone
   >>> arcade.get_timestamp(tzinfo=timezone.utc)
   '2024_12_11_1009_08_000007UTC`

Starting with Python 3.11, you can use :py:attr:`datetime.UTC` as a
more readable shortcut. However, the built-in date & time tools can
still be confusing and incomplete. To learn about the most popular
alternatives, see the heading below.


.. _debug-better-datetime:

Better Date & Time Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are plenty of excellent replacements for both
:py:func:`arcade.get_timestamp`and Python's :py:mod:`datetime`.

In addition to beautiful syntax, the best of them are
:ref:`backward compatible <strftime-strptime-behavior>` with
:py:mod:`datetime` types.

.. list-table::
   :header-rows: 1

   * - Library
     - Pros
     - Cons

   * - `Arrow <https://arrow.readthedocs.io/en/latest/index.html>`_
     - Very popular and mature
     - Fewer features

   * - `Pendulum <https://pendulum.eustace.io/docs/>`_
     - Popular and mature
     - Included by other libraries which build on it

   * - `Moment <https://github.com/zachwill/moment>`_
     - Well-liked and clean
     - "Beta-quality" according to creator

   * - `Maya <https://github.com/timofurrer/maya>`_
     - Clean syntax
     - `Currently unmaintained <https://github.com/timofurrer/maya/issues/197>`_
