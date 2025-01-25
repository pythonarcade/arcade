.. _currently supported by the PSF: https://devguide.python.org/versions/#supported-versions

Obsolete Python Versions
========================

Arcade aims to support the same Python versions
`currently supported by the PSF`_.

You are strongly encouraged to upgrade to one of the versions listed at the
link above, with the exception of 3.11 or later. Some of Arcade's dependencies
have not yet been ported for those versions.

If you absolutely cannot upgrade to Python 3.9 or later, you can try using an
older and unsupported version of Arcade.

Please remember the following:

#. Bugs will not be fixed, unless they are also present in current versions
#. The features and API may be very different from current versions
#. You will need use documentation for the version of Arcade you run

The pairings suggested below might not work. They are based on briefly skimming
git history.  You may have to use trial and error to look for a version that
works, and it's possible that you won't find one! Here be dragons!

======================= ======================== ===============
Obsolete Python Version Suggested Arcade Version Git Commit Hash
======================= ======================== ===============
3.8                     2.6.17                   6c4221c
3.7                     2.6.17                   6c4221c
3.6                     2.6.17                   6e0a9af
3.5                     1.2.2                    078f5be
======================= ======================== ===============

You can attempt to install these versions via the command line through pip,
or by installing from source from github. Check the tags on Arcade's
`github page <https://github.com/pythonarcade/arcade>`_ for additional commit
IDs.
