Shaders - Shadertoy
===================

.. _tutorials_shaders:

Shaders are small programs which specify how graphics hardware should
draw & shade objects. They offer power, flexibility, and efficiency far
beyond what you could achieve using shapes or :py:class:`~arcade.Sprite`
instances alone. The tutorials below serve as an introduction to shaders.

.. Note:: Note that "shadertoy" shaders is only a small subset of what is possible with
   shaders. Shadertoy shaders only use the pixel shader and will do everything
   in "screen space". There are other shaders using geometry and more generic compute
   processing. Arcade supports these as well, but they are not covered in this tutorial.

.. toctree::
   :maxdepth: 1

   raycasting/index
   crt_filter/index
   shader_toy_glow/index
   shader_toy_particles/index
   compute_shader/index
   gpu_particle_burst/index
   shader_inputs/index
