This logo of the snake doubles as a quick way to test Arcade's resource handles.

.. raw:: html

   <ol>
      <li>Look down toward the Arcade logo below until you see the file name</li>
      <li>Look to the right edge of the file name (<code class="docutils literal notranslate"><span class="pre">'logo.png'</span></code>)</li>
      <li>There should be a copy button (<div class="arcade-ezcopy doc-ui-example-dummy" style="display: inline-block;">
        <img src="/_static/icons/tabler/copy.svg"></div>) </li>
      <li>Click or tap it.</li>
   </ol>

Click the button or tap it if you're on mobile. Then try pasting in your favorite text editor. It
should look like this::

  ':resources:/logo.png'

This string is what Arcade calls a **:ref:`resource handle <resource_handles>`**. They let you load
images, sound, and other data without worrying about where exactly data is on a computer. To learn
more, including how to define your own handle prefix, see :ref:`resource_handles`.

To get started with game code right away, please see the following:

* :ref:`example-code`
* :ref:`main-page-tutorials`
