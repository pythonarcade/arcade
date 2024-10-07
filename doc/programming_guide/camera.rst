Camera
======

Introduction
------------

This guide aims to help you understand how cameras in modern games work without going in-depth on the maths.
Whenever concepts are glossed over links to external sources will be provided. The understanding this guide will provided
should carry over into any game making applications.

This guide is structured to get you up and running with :py:class:``arcade.Camera2D`` as quickly as possible before doing
a deep dive. If you would like a fuller understanding of Arcade's cameras it is strongly advised you follow through every example
as they built off of each other. 

Arcade has made design decisions that may differ from other game engines, when a concept is transferrable it will be made clear.
If you have any further questions do not hesitate to reach out on the Arcade discord.

Cameras 101
-----------

What is a camera?

CameraData (The titular 'camera')

ProjectionData (The projection volume)

~ Some of this is interoperable with other systems, but its pretty heavy on the arcade specifics

:py:class:``Camera2D``
----------------------

Using CameraData and a Camera2D.

If you just wanted to get a camera working you can stop here (exlcuding render targets)

~ This is all arcade

Cameras 102
-----------

grips, rotating, project, unproject, near/far plane.

This is all you need to use everything Camera2D provides, but I recommend reading the rest atleast once.

~ This is all arcdae except the project unproject stuff that's super useful for other systems

Coordinate Spaces
-----------------

What is a coordinate space, and how does it relate to Cameras.

bye bye pixels!

~ This isn't arcade specific, but will have arcade based examples and demos

Matrices
--------

How do we represent coordinate spaces, and how to we move between them.

explain the 4x4 matrix trick

Explain how these describe the projection volumes

view matrix

projection matrix

touch on how the perspecitve projection breaks linearity, but super lightly

~ This isn't arcade specific, but will have arcade based examples and demos 

Context Stack
-------------

Explain how arcade saves each frame's changes to the GL context

~ This is very arcade specific, and super nerdy

Offscreen Rendering
-------------------

Touch a little bit on offscreen rendering, doesn't actually need the previous chapters, 
but it is still an advanced topic and requires some GL understanding.

~ Arcade specific, but the framebuffer concepts are the same accross all of OpenGL

Projectors
----------

Just detail a bit on each projector and when it should be used (plus how to make them in the case of StaticProjector)

:py:class:`Camera2D`
^^^^^^^^^^^^^^^^^^^^

:py:class:`OrthographicProjector`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`PerspectiveProjector`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`ViewportProjector`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`DefaultProjector`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`StaticProjector`
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Grips
-----

Detail how the grips work and when to use them. Plus a little demo for each.

:py:func:`constrain_\<x\>`
^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:func:`rotate_around_\<x\>`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:func:`strafe`
^^^^^^^^^^^^^^^^^

:py:class:`ScreenShake2D`
^^^^^^^^^^^^^^^^^^^^^^^^^

The Camera Recipe Book
^^^^^^^^^^^^^^^^^^^^^^

Basically anything that you might want to do with a camera that either isn't in Arcade yet, or is too implementation sepcific.

Aspect Ratio, Split Screen, smooth pixel perfect, non-linear projections
