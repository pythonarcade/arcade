#!/usr/bin/env python

from os import path
import sys
from setuptools import setup

VERSION = 'default'
def execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)


# execute the file
execfile("arcade/version.py", locals=locals())

RELEASE = VERSION

if __name__ == "__main__":

    install_requires = [
        'pyglet',
        'pillow',
        'numpy',
        'pyglet-ffmpeg2',
        'pytiled-parser'
    ]
    if sys.version_info[0] == 3 and sys.version_info[1] == 6:
        install_requires.append('dataclasses')

    if "--format=msi" in sys.argv or "bdist_msi" in sys.argv:
        # hack the version name to a format msi doesn't have trouble with
        VERSION = VERSION.replace("-alpha", "a")
        VERSION = VERSION.replace("-beta", "b")
        VERSION = VERSION.replace("-rc", "r")

    fname = path.join(path.dirname(path.abspath(__file__)), "README.rst")
    with open(fname, "r") as f:
        long_desc = f.read()

    setup(
          name="arcade",
          version=RELEASE,
          description="Arcade Game Development Library",
          long_description=long_desc,
          author="Paul Vincent Craven",
          author_email="paul.craven@simpson.edu",
          license="MIT",
          url="http://arcade.academy",
          download_url="http://arcade.academy",
          install_requires=install_requires,
          packages=["arcade",
                    "arcade.key",
                    "arcade.color",
                    "arcade.csscolor",
                    "arcade.examples"
                    ],
          python_requires='>=3.6',
          classifiers=[
              "Development Status :: 5 - Production/Stable",
              "Intended Audience :: Developers",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent",
              "Programming Language :: Python",
              "Programming Language :: Python :: 3.6",
              "Programming Language :: Python :: 3.7",
              "Programming Language :: Python :: Implementation :: CPython",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
          test_suite="tests",
          package_data={'arcade': ['resources/gui_themes/Fantasy/Buttons/*',
                                   'resources/gui_themes/Fantasy/DialogueBox/*',
                                   'resources/gui_themes/Fantasy/Menu/*',
                                   'resources/gui_themes/Fantasy/TextBox/*',
                                   'resources/gui_themes/Fantasy/Window/*',
                                   'resources/images/*',
                                   'resources/images/alien/*',
                                   'resources/images/animated_characters/female_adventurer/*',
                                   'resources/images/animated_characters/female_person/*',
                                   'resources/images/animated_characters/male_adventurer/*',
                                   'resources/images/animated_characters/male_person/*',
                                   'resources/images/animated_characters/robot/*',
                                   'resources/images/animated_characters/zombie/*',
                                   'resources/images/backgrounds/*',
                                   'resources/images/enemies/*',
                                   'resources/images/isometric_dungeon/*',
                                   'resources/images/items/*',
                                   'resources/images/pinball/*',
                                   'resources/images/space_shooter/*',
                                   'resources/images/spritesheets/*',
                                   'resources/images/tiles/*',
                                   'resources/sounds/*',
                                   'resources/tmx_maps/*',
                                   'py.typed']},
          project_urls={
                        'Documentation': 'https://arcade.academy/',
                        'Example Code ': 'http://arcade.academy/examples/index.html',
                        'Issue Tracker': 'https://github.com/pvcraven/arcade/issues',
                        'Source': 'https://github.com/pvcraven/arcade',
                        'On-line Book': 'http://learn.arcade.academy/',
          },
         )
