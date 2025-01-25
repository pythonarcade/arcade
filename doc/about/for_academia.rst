.. _academia:

For Educators & Researchers
===========================

.. _citation template: https://github.com/pythonarcade/arcade#citation

Python Arcade was created by Paul V. Craven while teaching at Simpson College.

In addition to the main Arcade 3.0 documentation you are currently reading, there
are further resources to help academic users. These include:

* The :ref:`citation template <academia_citations>`
* A companion :ref:`academia_arcade_book` by Arcade's creator
* Potential 2.6.X maintenance releases to support curricula using Arcade 2.6


.. _academia_citations:

Citation Template
-----------------

Arcade provides a `citation template`_ in `BibTeX`_ format.

To learn more about using this template, please consult the following:

* the documentation of your reference management tool
* any style guides you are required to follow


.. _academia_version_2v3:

Version Considerations
----------------------
Most users will be better off using Arade 3.0.

The main case for continuing to use ``2.6.X`` releases is reliance on teaching
materials which have not yet been updated, including the :ref:`academia_arcade_book`.


.. _academia_arcade_book:

Arcade Book
^^^^^^^^^^^

The creator of Arcade wrote an `Arcade book`_ which covers Python basics in greater depth
than the main Arcade documentation.


It may be some time until the `Arcade book`_ is updated for Arcade 3.0. Doing so requires a
separate effort after the 3.0 release due to the the scale and number of changes since
Arcade 2.6.


Similarities to this Documentation
""""""""""""""""""""""""""""""""""

Both the book and the documentation you are currently reading provide:

* all-ages learning resources
* gentle introductions to Python and Arcade


Differences from this Documentation
"""""""""""""""""""""""""""""""""""

The book caters more heavily to beginners and educators by providing the following
in a traditional chapter and curriculum structure:

#. Embedded videos covering concepts and past student projects
#. Lab exercises to help apply chapter material through practice
#. Translations in `Swedish / Svenska <book_sv>`_ and `German / Deutsche <book_de>`_

It also offers gentle, beginner-friendly introductions to topics which can intimidate
even the graduates of college-level computer science programs:

#. Editors and development environments
#. Industry-standard version control tools
#. CS topics applicable at college-level and beyond


.. _2_6_maintenance:

2.6.X Maintenance?
------------------

The Arcade team is exploring additional *maintenance-only* releases for 2.6.X.

The goals for these still-hypothetical releases would be:

#. Security updates
#. Compatibility with newer Python versions
#. Highly limited bug fixes

Since the Arcade team's focus is on improving Arcade 3.0, no new features will be added
unless at least one of the following is true:

* It is required for a security or compatibilty improvement
* The effort required is minimal


Raspberry Pi and other SBCs
---------------------------

For educators, Single-Board Computers (SBCs) such as the Raspberry Pi 4 and 5
are not always the most cost-effective option.

However, they may be an attractive option when at least one of the following
applies:

* You have an educational discount
* You have grant or non-profit funding
* Surplus hardware isn't an option


.. _sbc_rule_of_thumb:

SBC Purchasing Rules of Thumb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: These rules help **non-experts** steer toward Arcade-copatible devices.

          You can find more in-depth descriptions of the required OpenGL ES versions
          and more under the :ref:`sbc_requirements` heading.


ARM64 and AMD64 are Easiest
"""""""""""""""""""""""""""

The :ref:`known-working Raspberry Pi 4 and 5 <sbc_supported_raspi>` are both ARM64
devices. If you are considering other boards due to price or availability, stick to
the following CPU architectures:

* ARM64
* AMD64 (same as most non-Mac desktop CPUs)

No RISC-based SBC has been verified as compatible. Although some *may* work,
SBCs based on RISC-V CPUs are likely to lack:

* introductory tutorials
* beginner-friendly documentation 



Credit Card Rule
""""""""""""""""

As of October 2024, all compatible and widely-available SBCs are
larger than credit cards:

* 3.375 inches by 2.125 inches
* 85.60 mm by 53.98 mm

If you try to use this rule:

#. Compare to the actual circuit board's size, not the size of the package
#. Use an old hotel key card, expired credit card, or expired debit card

It's unlikey that an SBC board will have magnets. However, the package
might include them in motors (in kits) or as part of the box itself.
Using an old card stops you from accidentally wiping a magnetic strip you need.

Although this errs on the side of caution, it also:

* quickly rules out :ref:`incompatible Raspberry Pi models <sbc_unsupported_raspis>`
* should apply to other SBCs as well
