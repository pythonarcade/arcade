#!/usr/bin/env python

from arcade import *

BUILD += 1

f = open('arcade/version.py', 'w')

version_info_string = """#!/usr/bin/env python

BUILD = {}
VERSION = "{}"
RELEASE = VERSION + "r" + str(BUILD)
""".format(BUILD, VERSION)
f.write(version_info_string)

f.close()


def update_file(filename):
    f = open(filename, 'r')

    file_contents = f.read()

    f.close()

    pos = 0
    for i in range(6):
        pos = file_contents.find("\n", pos + 1)

    file_contents = version_info_string + file_contents[pos:]

    f = open(filename, 'w')
    f.write(file_contents)
    f.close()

update_file('setup.py')
update_file('doc/conf.py')
