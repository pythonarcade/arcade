.. _vectors-and-matrices:

Vector & Matrix Overview
------------------------

.. warning:: This is an unfinished page!

             It will change rapidly.

Some things can't be expressed using just one number. For example:

* Where a game character is
* How that character moves every frame
* A color we'll draw their HP bar with

We can use vectors and matrices to store this data and do useful things
with it. Examples include:

* Moving characters or objects
* Rotating points around a center in 2D and 3D
* Finding points part-way between others


What's a Vector?
^^^^^^^^^^^^^^^^

Vectors are a general way to express things as groups of numbers.

They can be thought of and written in two equivalent ways:

* A **magnitude** (length) and a **direction**
* A number value for each dimension

.. list-table:: Common Examples of Vector Quantities
   :header-rows: 1

   * - Name
     - Plain English
     - Example / Details

   * - Position
     - Where something is
     - ``x=-1.0, y=5``

   * - Direction
     - A direction in space
     - ``x=1.4142, y=1.4142`` (see :ref:`def-unit-vector`)

   * - Velocity
     - How fast it's going in a specific direction
     - ``x=0.2, y=0.5``

   * - RGBA Color
     - Red, blue, green, and alpha (opacity)
     - :py:class:`Color(255, 127, 127, 255) <arcade.types.Color>`

.. _our_vector_types:

Our Vector Types
^^^^^^^^^^^^^^^^

Arcade often uses :py:mod:`pyglet.math`'s vector code.

The most common one is :py:class:`~pyglet.math.Vec2`. Like the others,
it's a special kind of :py:attr:`tuple`.

.. list-table::
   :header-rows: 1

   * - Difference
     - Example

   * - Individual elements are faster to access
       than indexing by number
     - :py:attr:`~arcade.Rect.center`'s
       :py:attr:`~pyglet.math.Vec2.x` and py:attr:`~pyglet.math.Vec2.y`

   * - Common math operations are supported
     - ``Vec2(1.0, 2.0) + Vec2(2.0, 3.0)``

See :py:class:`pyglet.math.Vec2` to learn more.
