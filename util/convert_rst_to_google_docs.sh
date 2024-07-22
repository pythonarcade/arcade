#!/bin/bash

# Easy Wrapper around the docconvert python package
# https://pypi.org/project/docconvert/

requires() {
cat <<EOF
Before using, please make sure to do the following:
1. Follow the contributor setup in CONTRIBUTING.md
2. pip install docconvert
EOF
}

if [ -z "$(which docconvert)" ]; then
  echo "ERROR: Couldn't find docconvert!" 1>&2
  requires 1>&2
  exit 1
fi


Usage() {
cat <<EOF
$0 FILE_OR_FILES ...

An easy wrapper around the Python-based docconvert utility.
https://pypi.org/project/docconvert/

EOF
requires
cat <<EOF

After setup, use as follows:

1. $0 arcade/name.py
2. ./make.py serve
3. look at the pages in browser to make sure they're good

EOF
}

if [ "$#" -eq 0 ] || [ "$1" == "--help" ]; then
  Usage
  exit 0
fi


CONFIG_FILE="docconvert.json"
ensure_have_config() {
if [ -f "$CONFIG_FILE" ]; then
  echo "Already have config file $CONFIG_FILE"
  return
fi

echo "Writing a default config file to $CONFIG_FILE"
# This is a default file which sort-of does a decent job on
# current versions of docconvert. You may want use "guess" for
# the input style in some cases, either via editing the json
# of the -i flag. See the Usage for docconvert to learn more:
# https://pypi.org/project/docconvert/
cat <<EOF > $CONFIG_FILE
{                                                                                                       
    "input_style": "rest",
    "output_style": "google",
    "accepted_shebangs": [
        "python"
    ],  
    "output": {
        "first_line": true,
        "remove_type_backticks": "false",
        "use_types": false
    }
}
EOF
}
ensure_have_config
echo "Attempting docconvert..."

docconvert --config $CONFIG_FILE --in-place "$@"
