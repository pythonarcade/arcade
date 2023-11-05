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
#. :ref:`sound-advanced-playback`
#. :ref:`sound-compat`
#. :ref:`sound-other-libraries` (for advanced users)

.. rubric:: I'm Impatient!

Users who want to skip to example code should consult the following:

#. :ref:`sound_demo`
#. :ref:`sound_speed_demo`
#. :ref:`music_control_demo`
#. :ref:`Platformer Tutorial - Step 7 - Add Coins And Sound <platformer_part_seven>`

   #. :ref:`platformer_part_seven_loading_sounds`
   #. :ref:`platformer_part_seven_playing_sounds`

.. _sound-why-important:

Why Is Sound Important?
-----------------------

Sound helps players make sense of what they see.

This is about far more than the game being immersive or cool. For
example, have you ever run into one of these common problems?

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

Before you can play a sound, you need to load its data into memory.

Arcade provides two ways to do this. Both accept the same arguments and
return an :py:class:`arcade.Sound` instance.

The easiest way to use :py:func:`arcade.load_sound`:

.. code-block:: python

    import arcade

    # You can pass strings containing a built-in resource handle,
    hurt_sound = arcade.load_sound(":resources:sounds/hurt1.wav")
    # a pathlib.Path,
    pathlib_sound = arcade.load_sound(Path("imaginary\\windows\\path\\file.wav"))
    # or an ordinary string describing a path.
    string_path_sound = arcade.load_sound("imaginary/mac/style/path.wav")

If you prefer a more object-oriented style, you can create
:py:class:`~arcade.Sound` instances directly:

.. code-block:: python

    from arcade import Sound  # You can also use arcade.Sound directly

    # Although Sound accepts the same arguments as load_sound,
    # only the built-in resource handle is shown here.
    hurt_sound = Sound(":resources:sounds/hurt1.wav")

See the following to learn more:

#. :ref:`Platformer Part 7 - Loading Sounds <platformer_part_seven_loading_sounds>`
#. :ref:`resources`
#. :py:mod:`pathlib`
#. :ref:`sound-loading-modes`

.. _sound-basics-playing:

Playing Sounds
^^^^^^^^^^^^^^

There are two easy ways to play a :py:class:`~arcade.Sound` object.

One is to call :py:meth:`Sound.play <arcade.Sound.play>` directly:

.. code-block:: python

    self.hurt_player = hurt_sound.play()

The other is to pass a :py:class:`~arcade.Sound` instance as the first
argument of :py:func:`arcade.play_sound`:

.. code-block:: python

    # Important: this *must* be a Sound instance, not a path or string!
    self.hurt_player = arcade.play_sound(hurt_sound)

Both return a :py:class:`pyglet.media.player.Player`. You should store
it somewhere if you want to be able to stop or alter a specific playback of
a :py:class:`~arcade.Sound`'s data.

``arcade.Sound`` vs pyglet's ``Player``
"""""""""""""""""""""""""""""""""""""""

This is a very important distinction:

* An :py:class:`arcade.Sound` represents a source of audio data
* Arcade uses pyglet's :py:class:`~pyglet.media.player.Player` to
  represent a specific playback of audio data

Imagine you have two non-player characters in a game which both play the
same :py:class:`~arcade.Sound` when moving. Since they are separate
characters in the world, they have separate playbacks of that sound.

This means each stores its own :py:class:`~pyglet.media.player.Player`
object to allow controlling its specific playback of the movement sound.
For example, one character may get close enough to the user's character
to talk, attack, or perform some other action. When a character stops
moving, you would use that character's specific pyglet
:py:class:`~pyglet.media.player.Player` to stop the corresponding
playback of the movement sound.

This is crucial for games which hide parts of the world from view.
Enemies without a way for users to detect their presence is the most
common version of the unknown danger mentioned in :ref:`sound-why-important`.

See the following to learn more:

#. :ref:`Platformer Tutorial - Part 7 - Collision Detection <platformer_part_seven_playing_sounds>`
#. :ref:`sound_demo`

.. _sound-basics-stopping:

Stopping Sounds
^^^^^^^^^^^^^^^

Arcade's helper functions are the easiest way to stop playback. To use them:

#. Do one of the following:

   * Pass the stored pyglet :py:class:`~pyglet.media.player.Player` to
     :py:func:`arcade.stop_sound`:

     .. code-block:: python

        arcade.stop_sound(self.current_playback)

   * Pass the stored pyglet :py:class:`~pyglet.media.player.Player` to the
     sound's :py:meth:`~arcade.Sound.stop` method:

     .. code-block:: python

        self.hurt_sound.stop(self.current_playback)

#. Clear any references to the player to allow its memory to be freed:

   .. code-block:: python

      # For each object, Python tracks how many other objects use it. If
      # nothing else uses an object, it will be marked as garbage which
      # Python can delete automatically to free memory.
      self.current_playback = None

See the following to learn more:

* :ref:`sound-compat-easy`
* :ref:`sound-advanced-playback`

.. _sound-loading-modes:

Streaming or Static Loading?
----------------------------

.. _keyword argument: https://docs.python.org/3/glossary.html#term-argument

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

By default, arcade decompresses the entirety of each sound into memory.

This is the best option for most game sound effects. It's called
"static" [#staticsourcefoot]_ audio because the data never changes.

The alternative is streaming. Enable it by passing ``True`` through the
``streaming`` `keyword argument`_  when you :ref:`load a sound
<sound-basics-loading>`::

    # Both loading approaches accept the streaming keyword.
    classical_music_track = arcade.load_sound(":resources:music/1918.mp3", streaming=True)
    funky_music_track = arcade.Sound(":resources:music/funkyrobot.mp3", streaming=True)


For an interactive example, see the :ref:`music_control_demo`.

The following subheadings will explain each option in detail.

.. [#meaningbestformatheader]
   See :ref:`sound-compat-easy` to learn more.

.. [#staticsourcefoot]
   See the :py:class:`pyglet.media.StaticSource` class used by arcade.

.. _sound-loading-modes-static:

Static Sounds Can Be Fastest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As long as you have enough memory, preloading entire sounds prevents
in-game slowdowns.

This is because disk access is one of the slowest things a computer can
do. Avoiding it during gameplay is important if your gameplay needs to
be fast and smooth.

However, storing full decompressed albums of music in RAM should be
avoided. Each decompressed minute of CD quality audio uses slightly
more than 10 MB of RAM. This adds up quickly, so you should strongly
consider :ref:`streaming <sound-loading-modes-streaming>` music from
compressed files instead.

Any of the following will suggest specific audio should be loaded
as a static effect:

* You need to start playback quickly in response to gameplay.
* Two or more "copies" of the sound can be playing at the same time.
* You will unpredictably restart or skip playback through the file.
* You need to automatically loop playback.
* The file is a short clip.

.. _sound-loading-modes-streaming:

Streaming Can Save Memory
^^^^^^^^^^^^^^^^^^^^^^^^^

Streaming audio from files is very similar to streaming video online.

Both save memory by keeping only part of a file into memory at any given
time. Even on the slowest recent hardware, this usually works if:

* You only stream one media source at a time.
* You don't need synchronize it closely with anything else.

Use Streaming Sparingly
"""""""""""""""""""""""
The best way to use streaming is to only use it when you need it.

Advanced users may be able to handle streaming multiple tracks at a
time. However, issues with synchronization & interruptions will grow
with the number and audio quality of the tracks involved.

If you're unsure, avoid streaming unless you can say yes to all of the
following:

#. The :py:class:`~arcade.Sound` will have at most one playback at a time.

#. The file is long enough to make it worth it.

#. Seeking (skipping to different parts) will be infrequent.

   * Ideally, you will never seek or restart playback suddenly.
   * If you do seek, the jumps will ideally be close enough to
     land in the same or next chunk.

See the following to learn more:

* :ref:`sound-advanced-playback-change-aspects-ongoing`
* The :py:class:`pyglet.media.StreamingSource` class used to implement
  streaming

.. _sound-loading-modes-streaming-freezes:

Streaming Can Cause Freezes
"""""""""""""""""""""""""""
Failing to meet the requirements can cause buffering issues.

Good compression can help, but it can't fully overcome it. Each skip outside
the currently loaded data requires reading and decompressing a replacement.

In the worst-case scenario, frequent skipping will mean constantly
buffering instead of playing. Although video streaming sites can
downgrade quality, your game will be at risk of stuttering or freezing.

The best way to handle this is to only use streaming when necessary.

.. _sound-advanced-playback:

Advanced Playback Control
-------------------------

.. _pyglet_controlling_playback: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#controlling-playback
.. _inconsistency_loop_issue: https://github.com/pythonarcade/arcade/issues/1915

Arcade's functions for :ref:`sound-basics-stopping` are convenience
wrappers around the passed pyglet :py:class:`~pyglet.media.player.Player`.

You can alter a playback of :py:class:`~arcade.Sound` data with more precision
by:

* Using the properties and methods of its :py:class:`~pyglet.media.player.Player`
  any time before playback has finished
* Passing keyword arguments with the same (or similar) names as the
  Player's properties when :ref:`playing the sound <sound-basics-playing>`.

Stopping via the Player Object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The simplest form of advanced control is pausing and resuming playback.

Pausing
"""""""
There is no stop method. Instead, call the :py:meth:`Player.pause()
<pyglet.media.player.Player.pause>` method:

.. code-block:: python

   # Assume this is inside an Enemy class subclassing arcade.Sprite
   self.current_player.pause()

Stopping Permanently
""""""""""""""""""""

.. _garbage collection: https://devguide.python.org/internals/garbage-collector/

After you've paused a player, you can stop playback permanently:

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

For a more in-depth explanation of references and auto-deletion, skim
the start of Python's page on `garbage collection`_. Reading the Abstract
section of this page should be enough to get started.

Changing Aspects of Playback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are more ways to alter playback than stopping. Some are more
qualitative. Many of them can be applied to both new and ongoing sound
data playbacks, but in different ways.

.. _sound-advanced-playback-change-aspects-ongoing:

Change Ongoing Playbacks via Player Objects
"""""""""""""""""""""""""""""""""""""""""""
:py:meth:`Player.pause() <pyglet.media.player.Player.pause>` is one of
many method and property members which change aspects of an ongoing
playback. It's impossible to cover them all here, especially given the
complexity of :ref:`positional audio <sound-other-libraries-pyglet-positional>`.

Instead, the table below summarizes a few of the most useful members in
the context of arcade. Superscripts link info about potential issues,
such as name differences between properties and equivalent keyword
arguments to arcade functions.

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
     - The scaling factor to apply to the original audio's volume. Must
       be between ``0.0`` (silent) and ``1.0`` (full volume).

   * - :py:attr:`~pyglet.media.player.Player.loop`
       [#inconsistencyloop]_
     - :py:class:`bool` property
     - ``False``
     - Whether to restart playback automatically after finishing. [#streamingnoloop]_

   * - :py:attr:`~pyglet.media.player.Player.pitch` [#inconsistencyspeed]_
     - :py:class:`float` property
     - ``1.0``
     - How fast to play the sound data; also affects pitch.

.. [#inconsistencyloop]
   :py:func:`arcade.play_sound` uses ``looping`` instead. See:

   *  :ref:`sound-advanced-playback-change-aspects-new`
   * `The related GitHub issue <inconsistency_loop_issue_>`_.

.. [#streamingnoloop]
   Looping is unavailable when ``streaming=True``; see `pyglet's guide to
   controlling playback <pyglet_controlling_playback_>`_.

.. [#inconsistencyspeed]
   Arcade's equivalent keyword for :ref:`sound-basics-playing` is ``speed``

.. _sound-advanced-playback-change-aspects-new:

Configure New Playbacks via Keyword Arguments
"""""""""""""""""""""""""""""""""""""""""""""
Arcade's helper functions for playing sound also accept keyword
arguments for configuring playback. As mentioned above, the names of
these keywords are similar or identical to those of properties on
:py:class:`~pyglet.media.player.Player`. See the following to learn
more:

* :py:func:`arcade.play_sound`
* :py:meth:`Sound.play() <arcade.Sound.play>`
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
#. :ref:`Adjusting playback volume and speed of playback <sound-advanced-playback>`

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
#. Nearly every system which can run arcade has a supported MP3 decoder.
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

There are 3 ways arcade can read audio data through pyglet:

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
.. _pyglet_pulseaudiobug: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#the-bug

As with formats, you can maximize compatibility by only using the lowest
common denominators among features. The most restrictive backends are:

* Mac's only backend, an OpenAL version limited to 16-bit audio
* PulseAudio on Linux, which has multiple limitations:

  * It lacks support for :ref:`positional audio <sound-other-libraries-pyglet-positional>`
  * It can `crash under certain circumstances <pyglet_pulseaudiobug_>`_
    when other backends will not:

    * Pausing / resuming in debuggers
    * Rarely and unpredictably when multiple sounds are playing

On Linux, the best way to deal with the PulseAudio bug is to `install
OpenAL <pyglet_openal_>`_. It will often already be installed as a
dependency of other packages.

Other differences between backends are less drastic. Usually, they will
be things like the specific positional features supported and the maximum
number of simultaneous sounds.

See the following to learn more:

* `Pyglet's Audio Backends <pyglet_audio_drivers_>`_
* :ref:`sound-other-libraries`

Choosing the Audio Backend
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _python_env_vars: https://www.twilio.com/blog/environment-variables-python

By default, arcade will try pyglet audio back-ends in the following
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

* It's guaranteed to work wherever arcade's sound support does.
* It offers far better control over media than arcade
* You may have already used parts of it directly for :ref:`sound-advanced-playback`

Note that :py:attr:`arcade.Sound`'s ``source`` attribute holds a
:py:class:`pyglet.media.Source`. This means you can start off by cleanly
using arcade's resource and sound loading with pyglet features as needed.

.. _sound-other-libraries-pyglet-positional:

Notes on Positional Audio
"""""""""""""""""""""""""
Positional audio is a set of features which automatically adjust sound
volumes across the channels for physical speakers based on in-game
distances.

Although pyglet exposes its support for this through its
:py:class:`~pyglet.media.player.Player`, arcade does not currently offer
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
