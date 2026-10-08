.. _gui_animations:

Animations
==========

.. admonition:: Experimental API

    The GUI animation stack lives in :py:mod:`arcade.gui.experimental` and
    may change within minor version updates without a deprecation period.
    Import the names from there, e.g.
    ``from arcade.gui.experimental import UIAnimatedGroup, rel``.

Animations bring a GUI to life: buttons that pop when hovered, menus that
fade in, titles that gently pulse. Arcade's GUI provides a small, high level
animation API for this, built around a single class:
:py:class:`~arcade.gui.experimental.UIAnimatedGroup` and its
:py:meth:`~arcade.gui.experimental.UIAnimatedGroup.animate` method.

.. code-block:: python

    # scale the group to 108% within 0.15 seconds, with a "back out" overshoot
    group.animate(scale=1.08, duration=0.15, ease=Easing.BACK_OUT)

This page walks you through everything you need to know, from the first tween
to staggered menu entrances.


Quick start
-----------

:py:class:`~arcade.gui.experimental.UIAnimatedGroup` wraps a single child
widget (or a whole subtree) and renders it into a cached surface. Its
transform properties can then be animated with
:py:meth:`~arcade.gui.experimental.UIAnimatedGroup.animate`. Pass the
**target values** as keyword arguments, and optionally a ``duration``
(seconds), an easing function and a ``delay``:

.. code-block:: python

    from arcade.anim import Easing
    from arcade.gui.experimental import UIAnimatedGroup

    group = UIAnimatedGroup(child=UIFlatButton(text="Play"))
    layout.add(group)

    # move the group to x=400 within half a second
    group.animate(offset_x=400, duration=0.5)

    # animate several properties at once with an easing curve
    group.animate(scale=1.0, alpha=255, duration=0.5, ease=Easing.BACK_OUT)

    # start after a delay (useful for staggered entrances)
    group.animate(alpha=255, duration=0.3, delay=0.2)

The animation always starts from the **current value** of the property, so
animations blend smoothly with whatever state the group is in. To animate
from a fixed value, set the property first:

.. code-block:: python

    group.alpha = 0
    group.animate(alpha=255, duration=0.3)   # fade in from fully transparent

Animations are updated automatically as long as the
:py:class:`~arcade.gui.UIManager` receives ``on_update`` events — no manual
update calls are needed.


What can be animated?
---------------------

:py:class:`~arcade.gui.experimental.UIAnimatedGroup` provides transform
properties which do **not** affect layouting. This is the recommended way to
animate widgets — the wrapped subtree is cached, so animating the group is
basically free:

.. list-table::
   :header-rows: 1

   * - Property
     - Effect
   * - ``scale``
     - Scale factor around ``anchor``
   * - ``angle``
     - Rotation in degrees around ``anchor``
   * - ``alpha``
     - Opacity of the whole subtree (0-255)
   * - ``offset_x`` / ``offset_y``
     - Visual translation, without affecting layout
   * - ``tint``
     - Color multiplier applied to the whole subtree

.. code-block:: python

    from arcade.gui.experimental import UIAnimatedGroup

    group = UIAnimatedGroup(child=UIFlatButton(text="Play"))
    layout.add(group)

    group.animate(angle=360, duration=0.6, ease=Easing.CUBIC)

Because the wrapped subtree is cached, animating the group itself is
basically free — the widgets inside are not re-rendered.

.. note::

    If you only need the cached rendering without the interactive states
    (``hovered``, ``pressed``, ``on_click``), use the non-interactive
    :py:class:`~arcade.gui.experimental.UIRenderGroup` instead.

.. warning::

    Any writable attribute holding a numeric value can technically be
    animated, but animating layout-controlled values like ``rect`` or
    ``center_x`` of a widget inside a :py:class:`~arcade.gui.UILayout` fights
    the layout — the next layout pass will undo your animation. Animate the
    group's transform properties instead.


Sequences
---------

:py:meth:`~arcade.gui.experimental.UIAnimatedGroup.animate` returns an
:py:class:`~arcade.gui.experimental.Animation`. Use
:py:meth:`~arcade.gui.experimental.Animation.then` to append steps which run
after the previous one finished:

.. code-block:: python

    # wiggle: right, left, back to center
    group.animate(angle=3, duration=0.06) \
        .then(angle=-3, duration=0.12) \
        .then(angle=0, duration=0.06)

A ``then()`` without properties acts as a pause:

.. code-block:: python

    group.animate(alpha=0, duration=0.5).then(duration=0.2).on_finish(arcade.exit)

Each step reads its start values when it begins, so sequences stay smooth
even if something else moved the property in between.


Repeating animations
--------------------

Use ``repeat`` and ``yoyo`` for idle animations like pulsing or swaying.
``yoyo=True`` plays the animation backwards to its start values,
``repeat=True`` repeats forever (or pass a number for a fixed count):

.. code-block:: python

    # gentle pulse: 100% -> 105% -> 100%, forever
    group.animate(scale=1.05, duration=0.6, ease=Easing.SINE, repeat=True, yoyo=True)

``repeat`` loops the **whole sequence**, including all ``then()`` steps:

.. code-block:: python

    # sway: lean right, swing left, back to center, forever
    group.animate(angle=2, duration=0.6, ease=Easing.SINE, repeat=True) \
        .then(angle=-2, duration=1.2, ease=Easing.SINE) \
        .then(angle=0, duration=0.6, ease=Easing.SINE)

For endless movement in one direction, use
:py:func:`~arcade.gui.experimental.rel` to animate **relative** to the
current value. Every iteration continues from where the last one ended:

.. code-block:: python

    from arcade.gui.experimental import rel

    # spin clockwise, one full rotation every 8 seconds, forever
    group.animate(angle=rel(-360), duration=8, repeat=True)


Reacting to hover and other state changes
-----------------------------------------

GUI animations are usually triggered by state changes — a group being
hovered, pressed or shown. :py:class:`~arcade.gui.experimental.UIAnimatedGroup`
is interactive itself: its ``hovered``, ``pressed`` and ``on_click`` states
are hit-tested against the group's **untransformed** rect, so the trigger
zone stays stable while the visuals scale or rotate. Bind to the group's
properties and start animations in the callback:

.. code-block:: python

    from arcade.gui import bind
    from arcade.gui.experimental import UIAnimatedGroup

    group = UIAnimatedGroup(child=UIFlatButton(text="Play"))

    def on_hover_change():
        if group.hovered:
            group.animate(scale=1.08, duration=0.15, ease=Easing.BACK_OUT)
        else:
            group.animate(scale=1.0, duration=0.15)

    bind(group, "hovered", on_hover_change)

Notice there is no cleanup code: starting a new animation **takes over its
properties** from other running animations. If the "grow" animation is still
running when the mouse leaves, the "shrink" animation simply takes over
``scale`` from the current value — other animations (and other properties of
the same animation) keep running untouched.

This means the natural way to change direction is to just start a new
animation.


Finishing and stopping
----------------------

Use :py:meth:`~arcade.gui.experimental.Animation.on_finish` to run code when
an animation completes, and
:py:meth:`~arcade.gui.experimental.Animation.stop` to cancel one:

.. code-block:: python

    # fade out the menu, then close the window
    group.animate(alpha=0, scale=0.8, duration=0.5, ease=Easing.SINE_IN) \
        .then(duration=0.1) \
        .on_finish(arcade.exit)

    # keep a handle to cancel later
    idle = group.animate(scale=1.05, duration=0.6, repeat=True, yoyo=True)
    ...
    idle.stop()   # leaves properties at their current values

``on_finish`` is not invoked for stopped or taken-over animations, and
endlessly repeating animations never finish.


Easing
------

Easing functions shape the speed of an animation over time. Arcade ships the
common set in :py:class:`arcade.anim.Easing` — each exists as ``NAME``
(in-out), ``NAME_IN`` and ``NAME_OUT`` variant:

``LINEAR``, ``SINE``, ``QUAD``, ``CUBIC``, ``QUART``, ``QUINT``, ``EXPO``,
``CIRC``, ``BACK``, ``ELASTIC``, ``BOUNCE``

As a rule of thumb: use ``*_OUT`` variants for entrances (fast start, soft
landing), ``*_IN`` variants for exits, and ``BACK_OUT`` or ``ELASTIC_OUT``
for playful pops. Any callable ``(t: float) -> float`` works as well.


A complete example
------------------

The example ``arcade.examples.gui.exp_animations`` combines everything from
this page into an animated main menu — staggered pop-in entrances, pulsing
and swaying idle animations, hover pops and a fade-out on quit:

.. code-block:: bash

    python -m arcade.examples.gui.exp_animations


Low level: transitions
----------------------

Under the hood, animations implement the
:py:class:`~arcade.gui.experimental.TransitionBase` protocol and are ticked
via :py:meth:`~arcade.gui.experimental.UIAnimatedGroup.add_transition`. The
low level building blocks in
:py:mod:`arcade.gui.experimental.transition` remain available for custom
behavior:

- :py:class:`~arcade.gui.experimental.TransitionAttr` - tween a single attribute
- :py:class:`~arcade.gui.experimental.TransitionAttrIncr` - tween an attribute by an increment
- :py:class:`~arcade.gui.experimental.TransitionAttrSet` - set a value after a time
- :py:class:`~arcade.gui.experimental.TransitionDelay` - wait
- :py:class:`~arcade.gui.experimental.TransitionChain` /
  :py:class:`~arcade.gui.experimental.TransitionParallel`
  - combine transitions sequentially (``+``) or in parallel (``|``)

They can be freely combined with
:py:class:`~arcade.gui.experimental.Animation` objects using the ``+`` and
``|`` operators. Most code should prefer
:py:meth:`~arcade.gui.experimental.UIAnimatedGroup.animate`.
