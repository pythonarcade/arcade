Working With Shaders
====================

Shaders are graphics programs that run on GPU and can be used for many varied 
purposes. 

Here we look at some very simple shader programs and learn how to pass data to 
and from shaders

Basic Arcade Program
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: empty_project.py
    :caption: Starting template
    :linenos:

Basic Shader Program
~~~~~~~~~~~~~~~~~~~~

From here we add a very basic shader and draw it to the screen. This shader 
simply sets color and alpha based on the horizontal coordinate of the pixel. 

We have to define vertex shader and fragment shader programs.

* Vertex shaders run on each passed coorninate and can modify it. Here we use it
  only to pass on the coordinate on to the fragment shader
* Fragment shaders set color for each passed pixel. Here we set a fixed color 
  for every pixel and vary alpha based on horizontal position

We need to pass the shader the pixel coordinates so create an object ``quad_fs``
to facilitate it.

.. literalinclude:: basic_shader.py
    :caption: Simple shader
    :linenos:
    :emphasize-lines: 14-16, 18-37, 49-52

Passing Data To The Shader
~~~~~~~~~~~~~~~~~~~~~~~~~~

To pass data to the shader program we can define 
`uniforms <https://www.khronos.org/opengl/wiki/Uniform_(GLSL)>`_. Uniforms are 
global shader variables that act as parameters passed from outside the shader 
program.

We have to define uniform within the shader and then register the python 
variable with the shader program before rendering.

It is important to make sure that the uniform type is appropriate for the data 
being passed.

.. literalinclude:: uniforms.py
    :caption: Uniforms
    :linenos:
    :emphasize-lines: 35-36, 41-42, 44-46, 58-59

Accessing Textures From The Shader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make the shader more useful we may wish to pass textures to it.

Here we create to textures (and associated framebuffers) and pass them to the 
shader as uniform sampler objects. Unlike other uniforms we need to assign a 
reference to an integer texture channel (rather than directly to the python 
object) and ``.use()`` the texture to bind it to that channel. 

.. literalinclude:: textures.py
    :caption: Textures
    :linenos:
    :emphasize-lines: 18-27, 34-36, 40, 47-50, 54-60, 65-67, 89-91

Drawing To Texture From The Shader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally we have an example of reading from and writing to the same texture with
a shader.

We use the ``with fbo:`` syntax to tell Arcade that we wish to render to the new
frambuffer rather than default one. 

Once the shader has updated the framebuffer we need to copy its contents to the 
screen to be displayed.

.. literalinclude:: texture_write.py
    :caption: Textures
    :linenos:
    :emphasize-lines: 22-30, 61-66, 68-69
