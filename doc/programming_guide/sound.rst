.. _Wave: https://en.wikipedia.org/wiki/WAV
.. _MP3: https://en.wikipedia.org/wiki/MP3

.. _Audacity: https://www.audacityteam.org/
.. _FFmpeg: https://ffmpeg.org/

.. _PyGame CE: https://pyga.me/
.. _SDL2: https://www.libsdl.org/

.. _pyglet media guide: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html
.. _positional audio: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#positional-audio
.. _pyglet's supported media types: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#supported-media-types
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

The easiest way is :py:func:`arcade.load_sound`::

    import arcade

    # You can pass strings containing a built-in resource handle,
    hurt_sound = arcade.load_sound(":resources:sounds/hurt1.wav")
    # a pathlib.Path,
    pathlib_sound = arcade.load_sound(Path("imaginary\windows\path\file.wav"))
    # or an ordinary string describing a path.
    string_path_sound = arcade.load_sound("imaginary/mac/style/path.wav")

If you prefer a more object-oriented style, you can create
:py:class:`~arcade.Sound` instances directly::

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

One is to call :py:meth:`Sound.play <arcade.Sound.play>` directly::

    hurt_player = hurt_sound.play()

The other is to pass a :py:class:`~arcade.Sound` instance as the first
argument of :py:func:`arcade.play_sound`::

    # Important: this *must* be a Sound instance, not a path or string!
    self.hurt_player = arcade.play_sound(hurt_sound)

Both return a :py:class:`pyglet.media.player.Player`. You should store
it somewhere if you want to be able to stop or alter a specific playback of
a :py:class:`~arcade.Sound`'s data.

Sounds vs pyglet Players
""""""""""""""""""""""""
This is a very important distinction:

* A :py:class:`~arcade.Sound` represents a source of playable data
* A pyglet :py:class:`~pyglet.media.player.Player` represents a
  specific playback of that data

Imagine you have two characters in a game which both play the same
:py:class:`~arcade.Sound` when moving. Since they are separate
characters in the world with separate playbacks of the sound,
each stores its own :py:class:`~pyglet.media.player.Player`.

This allows controlling their playbacks of the movement sound
separately. For example, one character may get close enough to the
user's character to talk, attack, or perform some other action.
You would use that character's pyglet :py:class:`~pyglet.media.player.Player`
to stop the movement sound's playback.

Although this may seem unimportant, it is crucial for games which hide
parts of the world from view. An enemy with no way to know it's there
is the most common version of the unknown danger example listed in
:ref:`sound-why-important`.

See the following to learn more:

#. :ref:`Platformer Tutorial - Part 7 - Collision Detection <platformer_part_seven_playing_sounds>`
#. :ref:`sound_demo`

.. _sound-basics-stopping:

Stopping Sounds
^^^^^^^^^^^^^^^

.. _garbage collection: https://devguide.python.org/internals/garbage-collector/

Arcade's helper functions are the easiest way to stop playback:

* The :py:func:`arcade.stop_sound` function
* The :py:meth:`Sound.stop <arcade.Sound.stop>` method of the
  sound data being played

To use them, do the following:

#. Pass the stored pyglet :py:class:`~pyglet.media.player.Player` to one of the helpers::

    # These are equivalent, but remember:
    # 1. You only need to use one of them
    # 2. You must pass the Player object, not the Sound object
    arcade.stop_sound(self.current_playback)
    Sound.stop(self.current_playback)

#. Clear any references to the player to allow its memory to be freed::

    # For each object, Python tracks how many other objects use it. If
    # nothing else uses an object, it will be marked as garbage which
    # Python can delete automatically to free memory.
    self.current_playback = None

See the following to learn more:

* :ref:`sound-compat-easy`
* :ref:`sound-advanced-playback`
* `Python's contributor guide article on garbage collection <garbage collection_>`_

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

Any of the following suggest a sound should be loaded as a static effect:

* You need to start playback quickly in response to gameplay.
* 2 or more "copies" of the sound can be playing at the same time.
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
* You don't try to closely synchronize it with anything else.

Use Streaming Sparingly
"""""""""""""""""""""""
The best way to use streaming is to only use it when you need it.

Advanced users may be able to handle streaming multiple tracks at a
time. However, issues with synchronization & interruptions will grow
with the number and audio quality of the tracks involved.

If you're unsure, avoid streaming unless you can say yes to all of the
following:

#. The :py:class:`~arcade.Sound` will have at most one playback at a time.
   [#streamingsource]_

#. The file is long enough to make it worth it.

#. Seeking (skipping to different parts) will be infrequent.

   * Ideally, you will never seek or restart playback suddenly
   * If you do skip, the jumps will ideally be close enough to
     land in the same or next chunk.

.. [#streamingsource]
   This is a requirement of the underlying :py:class:`pyglet.media.StreamingSource`.

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

You can alter the playback of a :py:class:`arcade.Sound`'s data by:

* Using properties and methods of a :py:class:`~pyglet.media.player.Player`
  any time before playback has finished
* Passing keyword arguments with the same (or similar) names as the
  Player's properties when :ref:`playing the sound <sound-basics-playing>`.

Stopping via the Player Object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can stop playback through its pyglet :py:meth:`pyglet.media.player.Player`
instead of the :ref:`stopping helpers <sound-basics-stopping>` as follows:

#. Call the player's :py:meth:`~pyglet.media.player.Player.pause`
   method.
#. Call the player's :py:meth:`~pyglet.media.player.Player.delete`
   method.
#. Make sure all references to the player are discarded to allow
   `garbage collection`_.

Changing Playback Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ongoing Playback
""""""""""""""""
The properties and methods of an ongoing playback's
:py:class:`pyglet.media.player.Player` allow changing aspects of it.

The table below summarizes the most commonly used ones. Superscripts
link explanations of inconsistencies, such as differences between names
of properties and their equivalent keyword arguments in arcade functions.

.. list-table::
   :header-rows: 1

   * - :py:class:`~pyglet.media.player.Player` Property
     - Type
     - Default
     - Purpose

   * - :py:attr:`~pyglet.media.player.Player.volume`
     - :py:class:`float`
     - ``1.0``
     - The scaling factor for the original sound data's volume. Must be
       between ``0.0`` (silent) and ``1.0`` (full volume).

   * - :py:attr:`~pyglet.media.player.Player.loop`
       [#inconsistencyloop]_
     - :py:class:`bool`
     - ``False``
     - Whether to restart playback automatically after finishing. [#streamingnoloop]_

   * - :py:attr:`~pyglet.media.player.Player.pitch` [#inconsistencyspeed]_
     - :py:class:`float`
     - ``1.0``
     - How fast to play back the sound; also affects pitch.

.. [#inconsistencyloop]
   :py:func:`arcade.play_sound` uses ``looping`` as a keyword instead of
   ``loop``; see `the related GitHub issue <inconsistency_loop_issue_>`_.

.. [#streamingnoloop]
   Looping is unavailable when ``streaming=True``; see `pyglet's guide to
   controlling playback <pyglet_controlling_playback_>`_.

.. [#inconsistencyspeed]
   Arcade's equivalent keyword for :ref:`sound-basics-playing` is ``speed``

These are only a few of :py:class:`~pyglet.media.player.Player`'s many
features. Consult its documentation and the `relevant section of the pyglet
media guide <pyglet_controlling_playback_>`_ to learn more.

Changing Parameters from the Start
""""""""""""""""""""""""""""""""""
You can alter playback when :ref:`sound-basics-playing` through `keyword
arguments <keyword argument>`_ with the same or similar names as the
properties mentioned above. See the following to learn more:

* :ref:`sound_speed_demo`
* :py:func:`arcade.play_sound`
* :py:meth:`Sound.play <arcade.Sound.play>`

.. _sound-compat:

Cross-Platform Compatibility
----------------------------

The sections below cover the easiest approach to compatibility.

You can try other options it if you need to. Be aware that doing so
requires grappling with the factors affecting audio compatibility:

#. The formats which can be loaded
#. The features supported by playback
#. The hardware, software, and settings limitations on the first two
#. The interactions of project requirements with all of the above

.. _sound-compat-easy:

The Most Reliable Formats & Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For most users, the best formats are the following ones:

* Use 16-bit PCM Wave (``.wav``) files for :ref:`sound effects <sound-loading-modes-static>`
* Use MP3 files for :ref:`long background audio like music <sound-loading-modes-streaming>`

As long as a user has working audio hardware and drivers, the following
basic features should work:

#. :ref:`sound-basics-loading` sound effects from Wave files
#. :ref:`sound-basics-playing` and :ref:`sound-basics-stopping`
#. :ref:`Adjusting playback volume and speed of playback <sound-advanced-playback>`

Advanced functionality or subsets of it may not, especially
`positional audio`_. To learn more, see the rest of this page and the
links below:

* :ref:`sound-compat-playback`
* :ref:`sound-compat-easy-converting`
* `pyglet's supported media types`_

.. _sound-compat-easy-best-effects:

Why 16-bit PCM Wave for Effects?
""""""""""""""""""""""""""""""""
Loading 16-bit PCM ``.wav`` ensures all users can load sound effects because:

#. pyglet :ref:`has built-in in support for this format <sound-compat-loading>`
#. :ref:`Some platforms can only play 16-bit audio <sound-compat-playback>`

There is another requirement if you want to use  `positional audio`_:
the files must be mono (single-channel) instead of stereo.

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
* `Pyglet's Supported Media Types <pyglet's supported media types_>`_

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

These should be able to handle converting from stereo to mono
for users who want to use `positional audio`_ . Consult their
documentation to learn how.

.. [#linuxlame]
   Linux users may need to `install the LAME MP3 encoder separately
   to export MP3 files <https://manual.audacityteam.org/man/faq_installing_the_lame_mp3_encoder.html>`_.

.. _sound-compat-loading:

Loading In-Depth
^^^^^^^^^^^^^^^^

There are 3 ways arcade can read audio data through pyglet:

#. The built-in pyglet ``.wav`` loading features
#. Platform-specific components or nearly-universal libraries
#. Supported cross-platform media libraries, such as PyOgg or `FFmpeg`_

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
   See `pyglet's supported media types`_ to learn more.

.. _sound-compat-playback:

Backends Determine Playback Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _pyglet_openal: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#openal
.. _pyglet_pulseaudiobug: https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#the-bug

As with formats, you can maximize compatibility by only using the lowest
common denominators among features. The most restrictive backends are:

* Mac's only backend, an OpenAL version limited to 16-bit audio
* PulseAudio on Linux, which has multiple limitations:

  * It lacks support for `positional audio <positional audio_>`_.
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

* `pyglet's audio driver overview <pyglet_audio_drivers_>`_
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
variable <python_env_vars>`_. The following rules apply to its value:

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

The most obvious choice is pyglet itself:

* It's guaranteed to work wherever arcade's sound support does.
* You are already familiar with using :py:class:`pyglet.media.player.Player`
  to control playback.
* It offers more control over media loading and playback than arcade.

If you are interested in porting to using pyglet directly, note that the
:py:attr:`arcade.Sound.source` attribute is exposed. This means you can
cleanly interface with pyglet code if you are porting code or want to use
arcade's built-in resource path resolution.

To learn more, consult the `pyglet media guide`_.

External Libraries
^^^^^^^^^^^^^^^^^^

Some users have reported success with using `PyGame CE`_ or `SDL2`_ to
handle sound. Both these and other libraries may work for you as well.
You will need to experiment since this isn't officially supported.
