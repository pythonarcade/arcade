.. _Wave: https://en.wikipedia.org/wiki/WAV
.. _MP3: https://en.wikipedia.org/wiki/MP3

.. _Audacity: https://www.audacityteam.org/
.. _FFmpeg: https://ffmpeg.org/

.. _PyGame CE: https://pyga.me/
.. _SDL2: https://www.libsdl.org/

.. _pyglet media guide: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html
.. _pyglet's guide to supported media types: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#supported-media-types
.. _pyglet_audio_drivers: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#choosing-the-audio-driver

.. _sound:

Sound
=====

This page will help you get started by covering the essentials of sound.

In addition each section's concepts, there may also be links to example
code and documentation.

#. :ref:`sound-why-important`
#. :ref:`sound-basics`

   * :ref:`sound-basics-loading`
   * :ref:`sound-basics-playing`
   * :ref:`sound-basics-stopping`

#. :ref:`sound-loading-modes`
#. :ref:`sound-intermediate-playback`
#. :ref:`sound-compat`
#. :ref:`sound-other-libraries` (for advanced users)

.. rubric:: I'm Impatient!

Users who want to skip to example code should consult the following:

#. :ref:`sound_demo`
#. :ref:`sound_speed_demo`
#. :ref:`music_control_demo`
#. :ref:`Platformer Tutorial - Step 9 - Adding Sound <platformer_part_nine>`

.. _sound-why-important:

Why Is Sound Important?
-----------------------

Sound helps players make sense of what they see.

For example, have you ever run into one of these common problems?

* Danger you never knew was there
* A character whose reaction seemed unexpected or out of place
* Items or abilities which appeared similar, but were very different
* An unclear warning or confirmation dialog

How much progress did it cost you? A few minutes? The whole playthrough?
More importantly, how did you feel? You probably didn't want to keep
playing.

You can use sound to prevent moments like these. In each example above,
the right audio can provide the information players need for the game
to feel fair.

.. _sound-basics:

Sound Basics
------------

.. _sound-basics-loading:

Loading Sounds
^^^^^^^^^^^^^^

.. py:currentmodule:: arcade.sound

To play audio, you must first load its data into a :py:class:`Sound`
object.

Arcade has two ways to do this:

* :py:func:`arcade.load_sound`
* :py:class:`arcade.Sound`

Both provide a :py:class:`Sound` instance and accept the same arguments:

.. list-table::
   :header-rows: 1

   * - Argument
     - Type
     - Meaning
   * - ``path``
     - :py:class:`str` **|** :py:class:`~pathlib.Path`
     - A sound file (may use :ref:`resource_handles`)
   * - ``streaming``
     - :py:class:`bool`
     - * ``True`` streams from disk
       * ``False`` loads the whole file

The simplest option is to use :py:func:`arcade.load_sound`:

.. code-block:: python

    from pathlib import Path
    import arcade

    # The path argument accepts paths prefixed with resources handle,
    from_handle_prefix = arcade.load_sound(":resources:sounds/hurt1.wav")
    # Windows-style backslash paths,
    from_windows_path = arcade.load_sound(Path(r"sounds\windows\file.wav"))
    # or pathlib.Path objects:
    from_pathlib_path = arcade.load_sound(Path("imaginary/mac/style/path.wav"))

For an object-oriented approach, create :py:class:`Sound` instances
directly:

.. code-block:: python

    from arcade import Sound  # You can also use arcade.Sound directly

    # For music files and ambiance tracks, streaming=True is usually best
    streaming_music_file = Sound(":resources:music/1918.mp3", streaming=True)

To learn more, please see the following:

#. :ref:`resources`
#. Python's built-in :py:class:`pathlib.Path`
#. :ref:`sound-loading-modes`

.. _sound-basics-playing:

Playing Sounds
^^^^^^^^^^^^^^

Arcade has two easy ways to play loaded :py:class:`Sound` data.

Imagine you've loaded the following built-in sound file:

.. code-block:: python

    COIN_SOUND = arcade.load_sound(":resources:sounds/coin1.wav")

The first way to play it is passing it to :py:func:`arcade.play_sound`:

.. code-block:: python

    self.coin_playback = arcade.play_sound(COIN_SOUND)

We store the return value because it is a special object which lets us
control this specific playback of the :py:class:`Sound` data.

.. important:: You **must** pass a :py:class:`Sound`, not a path!

               If you pass :py:func:`arcade.play_sound` anything other
               than a :py:class:`Sound` or ``None``, it will raise a
               :py:class:`TypeError`.

To avoid making this mistake, you can call the :py:class:`Sound`
data's :py:meth:`Sound.play` method instead:

.. code-block:: python

    self.coin_playback = COIN_SOUND.play()


In each case, the returned object allows stopping and changing a specific playback
of a sound before it finishes. We'll cover this in depth below.

.. _sound-basics-stopping:

Stopping Sounds
^^^^^^^^^^^^^^^

.. _sound-basics-sound_vs_player:

Sound data vs Playbacks
"""""""""""""""""""""""

Arcade uses the :py:mod:`pyglet` multimedia library to handle sound.

Each playback of a :py:class:`Sound` has its own |pyglet Player| object
to control it:

.. code-block:: python

   # We can play the same Sound one, two, or many more times at once
   self.coin_playback_1 = arcade.play_sound(COIN_SOUND)
   self.coin_playback_2 = COIN_SOUND.play()
   self.coin_playback_3 = COIN_SOUND.play()
   ...


We can create and control a very large number of separate playbacks.
Although there is a platform-dependent upper limit, it is high enough
to be irrelevant for most games.

Stopping a Specific Playback
""""""""""""""""""""""""""""

There are two easy ways of stopping a playback of a :py:class:`Sound`.

The first is to choose which function we'll pass its
:py:class:`~pyglet.media.player.Player` object to:

* :py:func:`arcade.stop_sound`:

  .. code-block:: python

     arcade.stop_sound(self.coin_playback_1)


* The :py:class:`Sound` data's :py:meth:`Sound.stop`
  method:

  .. code-block:: python

     self.COIN_SOUND.stop(self.coin_playback_1)

The last step is to clean up by removing all remaining references to it:

.. code-block:: python

   # Overwriting them with None is the clearest option
   self.current_playback = None

By default, Python automatically counts how many places use an object.
When there are zero of these "references" left, Python will mark an
object as "garbage" and delete it automatically. This is called "garbage
collection." We'll cover it further in the advanced sections below.

To learn more about playback limits and stopping, please see the following:

* :ref:`sound-compat-easy`
* :ref:`sound-intermediate-playback`
* :ref:`sound_demo`


Intermediate Loading and Playback
---------------------------------

Arcade also offers more advanced options for controlling loading and playback.

These allow loading files in special modes best used for music. They also allow
controlling volume, speed, and spatial aspects of playback.

.. _sound-loading-modes:

Streaming or Static Loading?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _keyword argument: https://docs.python.org/3/glossary.html#term-argument

The streaming option is best for long-playing music and ambiance tracks.

.. list-table::
   :header-rows: 1

   * - Streaming
     - Best [#meaningbestformatheader]_ Format
     - Decompressed
     - Best Uses

   * - ``False`` (Default)
     - ``.wav``
     - Whole file
     - 2+ overlapping playbacks, short, repeated, unpredictable

   * - ``True``
     - ``.mp3``
     - Predicted data
     - 1 copy & file at a time, long, uninterrupted

Arcade uses **static** loading by default. It is called static loading
because it decompresses the whole audio file into memory once and then
never changes the data. Since the data never changes, it has multiple
benefits like allowing multiple playbacks at once.

The alternative is streaming. Although it saves memory for long music and
ambiance tracks, it has downsides:

* Only one playback of the :py:class:`Sound` permitted
* Moving around in the file can cause buffering issues
* Looping is not supported

Enable it by passing ``True`` through the ``streaming`` `keyword argument`_
when :ref:`loading sounds <sound-basics-loading>`:

.. code-block:: python

    # Both loading approaches accept the streaming keyword.
    classical_music_track = arcade.load_sound(":resources:music/1918.mp3", streaming=True)
    funky_music_track = arcade.Sound(":resources:music/funkyrobot.mp3", streaming=True)


To learn more about streaming, please see:

* The :ref:`music_control_demo` for runnable example code
* The :ref:`loading_performance_sound` guide for extensive discussion

.. [#meaningbestformatheader]
   See :ref:`sound-compat-easy` to learn more.

.. _sound-intermediate-playback:

Intermediate-Level Playback Control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Stopping via the Player Object
""""""""""""""""""""""""""""""

.. _pyglet_controlling_playback: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#controlling-playback

Arcade's :ref:`sound-basics-stopping` functions wrap |pyglet Player| features.

For additional finesse or less functional call overhead, some users
may want to access its functionality directly.

.. rubric:: Pausing

There is no stop method. Instead, call
:py:meth:`Player.pause() <pyglet.media.player.Player.pause>`:

.. code-block:: python

   # Assume this is inside a class which stores a pyglet Player
   self.current_player.pause()

.. rubric:: Stopping Permanently

.. _garbage collection: https://devguide.python.org/internals/garbage-collector/

After you've paused a player, you can stop playback permanently as follows:

#. Call the player's :py:meth:`~pyglet.media.player.Player.delete` method:

   .. code-block:: python

      # Permanently deletes the operating system half of this playback.
      self.current_player.delete()

   `This specific playback is now permanently over, but you can start
   new ones.`

#. Make sure all references to the player are replaced with ``None``:

   .. code-block:: python

      # Python will delete the pyglet Player once there are 0 references to it
      self.current_player = None

.. note:: This is how :py:class:`Sound.stop <arcade.Sound.stop>` works internally.

For a more in-depth explanation of references and auto-deletion, skim
the start of Python's page on `garbage collection`_. Reading the Abstract
section of this page should be enough to get started.


.. _sound-intermediate-playback-arguments:

Advanced Playback Arguments
"""""""""""""""""""""""""""
There are more ways to alter playback than stopping. Some are more
qualitative. Many of them can be applied to both new and ongoing sound
data playbacks, but in different ways.

Both :py:func:`play_sound` and :py:meth:`Sound.play` support the
following advanced arguments:

.. list-table::
   :header-rows: 1

   * - Argument
     - Values
     - Meaning

   * - :py:attr:`~pyglet.media.player.Player.volume`
     - :py:class:`float` between ``0.0`` (silent) and
       ``1.0`` (full volume)
     - A scaling factor for the original audio file.

   * - :py:attr:`~pyglet.media.player.Player.pan`
     - A :py:class:`float` between ``-1.0`` (left)
       and ``1.0`` (right)
     - The left / right channel balance

   * - ``loop``
     - :py:class:`bool` (``True`` / ``False``)
     - Whether to restart playback automatically after finishing.
       [#streamingnoloop]_

   * - ``speed``
     - :py:class:`float` greater than ``0.0``
     - The scaling factor for playback speed (and pitch)

       * Lower than ``1.0`` slows speed and lowers pitch
       * Exactly ``1.0`` is the original speed (default)
       * Higher than ``1.0`` plays faster with higher pitch

.. [#streamingnoloop]
   Looping is unavailable for :ref:`streaming <sound-loading-modes>`
   :py:class:`Sound` objects.


.. _sound-intermediate-playback-change-aspects-ongoing:

Change Ongoing Playbacks via Player Objects
"""""""""""""""""""""""""""""""""""""""""""
:py:meth:`Player.pause() <pyglet.media.player.Player.pause>` is one of
many method and property members which change aspects of an ongoing
playback. It's impossible to cover them all here, especially given the
complexity of :ref:`positional audio <sound-other-libraries-pyglet-positional>`.

Instead, the table below summarizes a few of the most useful members in
the context of Arcade. Superscripts link info about potential issues,
such as name differences between properties and equivalent keyword
arguments to Arcade functions.

.. list-table::
   :header-rows: 1

   * - :py:class:`~pyglet.media.player.Player` Member
     - Type
     - Default
     - Purpose

   * - :py:meth:`~pyglet.media.player.Player.pause`
     - method
     - N/A
     - Pause playback resumably.

   * - :py:meth:`~pyglet.media.player.Player.play`
     - method
     - N/A
     - Resume paused playback.

   * - :py:meth:`~pyglet.media.player.Player.seek`
     - method
     - N/A
     - .. warning:: :ref:`Using this option with streaming can cause freezes!
        <sound-loading-modes-streaming-freezes>`

       Skip to the passed :py:class:`float` timestamp measured as seconds
       from the audio's start.

   * - :py:attr:`~pyglet.media.player.Player.volume`
     - :py:class:`float` property
     - ``1.0``
     - A scaling factor for playing the audio between
       ``0.0`` (silent) and ``1.0`` (full volume).

   * - :py:attr:`~pyglet.media.player.Player.loop`
     - :py:class:`bool` property
     - ``False``
     - Whether to restart playback automatically after finishing. [#streamingnoloop2]_

   * - :py:attr:`~pyglet.media.player.Player.pitch` [#inconsistencyspeed]_
     - :py:class:`float` property
     - ``1.0``
     - How fast to play the sound data; also affects pitch.

.. [#streamingnoloop2]
   Looping is unavailable when ``streaming=True``; see `pyglet's guide to
   controlling playback <pyglet_controlling_playback_>`_.

.. [#inconsistencyspeed]
   Arcade's equivalent keyword for :ref:`sound-basics-playing` is ``speed``

.. _sound-intermediate-playback-change-aspects-new:

Configure New Playbacks via Keyword Arguments
"""""""""""""""""""""""""""""""""""""""""""""
Arcade's helper functions for playing sound also accept keyword
arguments for configuring playback. As mentioned above, the names of
these keywords are similar or identical to those of properties on
:py:class:`~pyglet.media.player.Player`. See the following to learn
more:

* :py:func:`arcade.play_sound`
* :py:meth:`Sound.play`
* :ref:`sound_speed_demo`

.. _sound-compat:

Cross-Platform Compatibility
----------------------------

The sections below cover the easiest approach to compatibility.

You can try other options if you need to. Be aware that doing so
requires grappling with the many factors affecting audio compatibility:

#. The formats which can be loaded
#. The features supported by playback
#. The hardware, software, and settings limitations on the first two
#. The interactions of project requirements with all of the above

.. _sound-compat-easy:

The Most Reliable Formats & Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For most users, the best approach to formats is:

* Use 16-bit PCM Wave (``.wav``) files for :ref:`sound effects <sound-loading-modes-static>`
* Use MP3 files for :ref:`long background audio like music <sound-loading-modes-streaming>`

As long as a user has working audio hardware and drivers, the following
basic features should work:

#. :ref:`sound-basics-loading` sound effects from Wave files
#. :ref:`sound-basics-playing` and :ref:`sound-basics-stopping`
#. :ref:`Adjusting playback volume and speed of playback <sound-intermediate-playback>`

Advanced functionality or subsets of it may not, especially
:ref:`positional audio <sound-other-libraries-pyglet-positional>`.
To learn more, see the rest of this page and `pyglet's guide to
supported media types`_.

.. _sound-compat-easy-best-effects:

Why 16-bit PCM Wave for Effects?
""""""""""""""""""""""""""""""""
Storing sound effects as 16-bit PCM ``.wav`` ensures all users can load them:

#. pyglet :ref:`has built-in in support for this format <sound-compat-loading>`
#. :ref:`Some platforms can only play 16-bit audio <sound-compat-playback>`

The files must also be mono rather than stereo if you want to use
:ref:`positional audio <sound-other-libraries-pyglet-positional>`.

Accepting these limitations is usually worth the compatibility benefits,
especially as a beginner.

.. _sound-compat-easy-best-stream:

Why MP3 For Music and Ambiance?
"""""""""""""""""""""""""""""""
#. Nearly every system which can run Arcade has a supported MP3 decoder.
#. MP3 files are much smaller than Wave equivalents per minute of audio,
   which has multiple benefits.

See the following to learn more:

* :ref:`sound-compat-loading`
* `Pyglet's Supported Media Types <pyglet's guide to supported media types_>`_

.. _sound-compat-easy-converting:

Converting Audio Formats
""""""""""""""""""""""""
Don't worry if you have a great sound in a different format.

There are multiple free, reliable, open-source tools you can use to
convert existing audio. Two of the most famous are summarized below.

.. list-table::
   :header-rows: 1

   * - Name & Link for Tool
     - Difficulty
     - Summary

   * - `Audacity`_
     - Beginner [#linuxlame]_
     - A free GUI application for editing sound

   * - `FFmpeg`_'s command line tool
     - Advanced
     - Powerful media conversion tool included with the library

Most versions of these tools should handle the following common tasks:

* Converting audio files from one encoding format to another
* Converting from stereo to mono for use with :ref:`positional audio
  <sound-other-libraries-pyglet-positional>`.

To integrate FFmpeg with Arcade as a decoder, you must use FFmpeg
version 4.X, 5.X, or 6.X. See :ref:`sound-compat-loading` to learn more.

.. [#linuxlame]
   Linux users may need to `install the LAME MP3 encoder separately
   to export MP3 files <https://manual.audacityteam.org/man/faq_installing_the_lame_mp3_encoder.html>`_.

.. _sound-compat-loading:

Loading In-Depth
^^^^^^^^^^^^^^^^

.. _pyglet_ffmpeg_install: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#ffmpeg-installation

There are 3 ways Arcade can read audio data through pyglet:

#. The built-in pyglet ``.wav`` loading features
#. Platform-specific components or nearly-universal libraries
#. Supported cross-platform media libraries, such as PyOgg or `FFmpeg`_

To load through FFmpeg, you must install FFmpeg 4.X, 5.X, or 6.X. This
is a requirement imposed by pyglet. See `pyglet's notes on installing
FFmpeg <pyglet_ffmpeg_install_>`_ to learn more.

Everyday Usage
""""""""""""""
In practice, Wave is universally supported and MP3 nearly so. [#mp3linux]_

Limiting yourself to these formats is usually worth the increased
compatibility doing so provides. Benefits include:

#. Smaller download & install sizes due to having fewer dependencies
#. Avoiding binary dependency issues common with PyInstaller and Nuitka
#. Faster install and loading, especially when using MP3s on slow drives

These benefits become even more important during game jams.

.. [#mp3linux]
   The only time MP3 will be absent is on unusual Linux configurations.
   See `pyglet's guide to supported media types`_ to learn more.

.. _sound-compat-playback:

Backends Determine Playback Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _pyglet_openal: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#openal

As with formats, you can maximize compatibility by only using the lowest
common denominators among features. The most restrictive backends are:

* Mac's only backend, an OpenAL version limited to 16-bit audio
* PulseAudio on Linux, which lacks support for common features such as
  :ref:`positional audio <sound-other-libraries-pyglet-positional>`.

On Linux, the best way to deal with the PulseAudio backend's limitations
is to `install OpenAL <pyglet_openal_>`_. It will often already be installed
as a dependency of other packages.

Other differences between backends are less drastic. Usually, they will
be things like the specific positional features supported and the maximum
number of simultaneous sounds.

See the following to learn more:

* `Pyglet's Audio Backends <pyglet_audio_drivers_>`_
* :ref:`sound-other-libraries`

Choosing the Audio Backend
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _python_env_vars: https://www.twilio.com/blog/environment-variables-python

By default, Arcade will try pyglet audio back-ends in the following
order until it finds one which loads:

#. ``"openal"``
#. ``"xaudio2"``
#. ``"directsound"``
#. ``"pulse"``
#. ``"silent"``

You can override through the ``ARCADE_SOUND_BACKENDS`` `environment
variable <python_env_vars_>`_. The following rules apply to its value:

#. It must be a comma-separated string
#. Each name must be an audio back-ends supported by pyglet
#. Spaces do not matter and will be ignored

For example, you could need to test OpenAL on a specific system. This
example first tries OpenAL, then gives up instead using fallbacks.

.. code-block:: shell

   ARCADE_SOUND_BACKENDS="openal,silent" python mygame.py

Please see the following to learn more:

* `pyglet's audio driver documentation <pyglet_audio_drivers_>`_
* `Working with Environment Variables in Python <python_env_vars_>`_

.. _sound-other-libraries:

Other Sound Libraries
---------------------

Advanced users may have reasons to use other libraries to handle sound.

.. _sound-other-libraries-pyglet:

Using Pyglet
^^^^^^^^^^^^
The most obvious external library for audio handling is pyglet:

* It's guaranteed to work wherever Arcade's sound support does.
* It offers far better control over media than Arcade
* You may have already used parts of it directly for :ref:`sound-intermediate-playback`

Note that :py:class:`Sound`'s :py:attr:`~Sound.source` attribute holds a
:py:class:`pyglet.media.Source`. This means you can start off by cleanly
using Arcade's resource and sound loading with pyglet features as needed.

.. _sound-other-libraries-pyglet-positional:

Notes on Positional Audio
"""""""""""""""""""""""""
Positional audio is a set of features which automatically adjust sound
volumes across the channels for physical speakers based on in-game
distances.

Although pyglet exposes its support for this through its
:py:class:`~pyglet.media.player.Player`, Arcade does not currently offer
integrations. You will have to do the setup work yourself.

.. _pyglet_positional_guide: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#positional-audio

If you already have some experience with Python, the following sequence
of links should serve as a primer for trying positional audio:

#. :ref:`sound-compat-easy-best-effects`
#. :ref:`sound-compat-playback`
#. The following sections of pyglet's media guide:

   #. `Controlling playback <pyglet_controlling_playback_>`_
   #. `Positional audio <pyglet_positional_guide_>`_

#. :py:class:`pyglet.media.player.Player`'s full documentation

External Libraries
^^^^^^^^^^^^^^^^^^

Some users have reported success with using `PyGame CE`_ or `SDL2`_ to
handle sound. Both these and other libraries may work for you as well.
You will need to experiment since this isn't officially supported.
