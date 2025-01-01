.. _faq:

Frequently asked questions
==========================

.. _faq_education:

Can I use Arcade resources in my own educational materials?
-----------------------------------------------------------

.. _gh_license: https://github.com/pythonarcade/arcade/blob/development/license.rst

Yes! Arcade was originally developed for educational use. In addition to
a page :ref:`academia`, we have further documentation covering:


* The :ref:`permissive_mit` covers the library and documentation
* The :ref:`CC0 Public Domain Dedication <permissive_almost_all_public>` and similar cover the :ref:`resources`

.. _faq_commercial:

Can I use Arcade in a commercial project?
-----------------------------------------

:ref:`commercial_games`. There's already one commercially released game using Arcade.

.. _faq-copying:

Can I copy and adapt example code for my own projects?
------------------------------------------------------

Of course! We encourage you to do so. That's why the example code is there: we
want you to learn and be successful. See the :ref:`permissive_mit` section to learn
more about Arcade's license means (you agree not to claim you wrote the whole thing).

Can Arcade run on...?
---------------------

Windows, Mac, and Linux
^^^^^^^^^^^^^^^^^^^^^^^

Yes. Most hardware with an Intel or AMD processor from the last ten years will do fine.
New :ref:`requirements_mac_mseries` can have some hiccups, but they generally work.

.. _faq-raspi:

Raspberry Pi and Other SBCs
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raspberry Pi is a popular brand of Single Board Computers (SBCs).

The Raspberry Pi 4 and 5 can run Arcade under `Raspberry Pi OS`_,
and the Raspberry Pi 400 *may* also work. As of October 2024,
:ref:`All other other Raspberry Pi models are incompatible <sbc_unsupported_raspis>`.

Other SBCs *may* work with Arcade 3.0.0. See the :ref:`sbc_requirements` to learn more.

.. _faq_web:

Web
^^^
Not yet. For the moment, the Arcade and `pyglet`_ teams are eagerly
watching ongoing developments in `WebGPU`_ and its `WASM`_ integrations.

.. _WebGPU: https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API
.. _WASM: https://developer.mozilla.org/en-US/docs/WebAssembly

.. _faq_mobile:

Mobile
^^^^^^
Not in the near future. Supporting mobile requires big changes to both
Arcade and the `pyglet`_ library we use.

.. _faq_android:

Android
"""""""
Android support will take a huge amount of work:

#. `pyglet`_ would need to account for mobile-specific OS behavior
#. Arcade would need to make changes to account for mobile as well
#. Not all devices will support the necessary :ref:`OpenGL ES versions <requirements_gles>`.

.. _faq_ios:
.. _faq_ipad:

iOS and iPad
""""""""""""

Not in the foreseeable future. They are much trickier than web or Android
for a number of reasons. For near-future iOS and iPad support, you may want to
to try `Kivy`_.

.. _Kivy: https://kivy.org

