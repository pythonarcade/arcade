.. _permissively_licensed:

Freedom to Remix and Share
==========================

Arcade makes sure you are free to build and share without worrying about fees or licenses.

All parts of the library are available free of charge and without
complicated red tape:

* Arcade's code uses the widely-adopted commercial-friendly
  :ref:`MIT License <permissive_mit>`
* The :ref:`resources` are high-quality and don't require attribution

.. _commercial_games:

Yes, You Can Make Commercial Games!
-----------------------------------

There is already a commercially available game made with Arcade.

`Spelly Cat`_ is a puzzle game available via Valve Software's `Steam marketplace <Steam>`_.
It is currently available for Windows and Linux.

.. important:: Arcade is currently a desktop-focused framework.

               :ref:`Web <faq_web>`, :ref:`Android <faq_android>`, :ref:`iPad <faq_ipad>`,
               and :ref:`iOS <faq_ios>` are not currently supported.

How Do I Publish My Games?
^^^^^^^^^^^^^^^^^^^^^^^^^^

It takes require patience, experimentation, and persistence.

You will need to tinker with packaging and platform-specific application signing
approaches in addition to gameplay. The following tutorials and documentation will
help you get started on bundling:

* :ref:`compile_with_nuitka`
* :ref:`bundle_into_redistributable`
* :ref:`resource_handles_one_file_builds`

You will also need to consult the platform documentation for any app store and achievements
tracker you use.

.. tip:: Even the Arcade maintainers have trouble with this!

          If you get stuck or frustrated, that's okay. Breathe deep, and remember
          that you can always :ref:`politely ask for help <how-to-get-help>`.

.. _Spelly Cat: https://store.steampowered.com/app/2445350/Spelly_Cat/
.. _Steam: https://store.steampowered.com/games/

.. _permissive_mit:

The MIT License
---------------

In addition to the ``arcade`` package on `PyPI`_, the source code
is available for modification and :ref:`contributions <how-to-contribute>`
under the `OSI-Approved MIT License`_. Roughly speaking, that means
using Arcade is an agreement to the following:

* You won't claim you wrote the whole library yourself
* You understand Arcade's features may have bugs

.. tip:: If you see a bug or a typo, we love :ref:`contributing-bug-reports`.

For more information on the MIT license, please see the following for a quick intro:

* https://www.tldrlegal.com/license/mit-license
* https://choosealicense.com/licenses/mit/

.. _OSI-Approved MIT License: https://opensource.org/license/mit

.. _permissive_almost_all_public:

Public Domain Assets
--------------------

Arcade's :ref:`resources` are carefully hand-picked to meet three criteria:

* High quality
* Friendly style
* Public domain (or as close as possible)

This means that unless you're in Academia, you don't have to worry. The licenses and attribution
are all taken care of since we only ship built-in resources which minimize the requirements for you.
If something requires special handling, we'll warn you about it.

Where are all these assets from?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mostly from `Kenney.nl <Kenney_nl>`_. Kenny is famous for creating a repository of free, high-quality
`CC0`_ (public domain) game assets. His work is funded by donations and
`Kenney's Patreon <https://www.patreon.com/kenney>`_.

Unlike other `Creative Commons licenses`_, the `CC0`_ doesn't impose terms or conditions.
It's the lawyer version saying the following:

.. raw:: html

   <blockquote><i>"I give permission to everyone to use this for whatever. Go make something cool!"</i></blockquote>

Although Arcade includes a few bundled assets which aren't from `Kenny.nl <Kenney_nl>`_, we've made sure
they're released under a similar license.


What About Academia?
--------------------

In addition to the MIT License, academics are expected to cite things.

Don't worry, we've got that covered too. In fact, we have an entire page :ref:`academia`.
It covers crucial topics, such as:

#. :ref:`academia_citations`
#. :ref:`academia_version_2v3`
#. :ref:`2_6_maintenance`
