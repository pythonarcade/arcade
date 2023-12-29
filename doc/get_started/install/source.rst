Installation From Source
========================

First step is to clone the repository:

.. code-block:: bash

    git clone https://github.com/pythonarcade/arcade.git

Or download from:

    https://github.com/pythonarcade/arcade/archive/development.zip

Next, we'll create a linked install. This will allow you to change files in the
arcade directory, and is great
if you want to modify the Arcade library code. From the root directory of
arcade type:

.. code-block:: bash

    pip install -e .

To install additional documentation and development requirements:

.. code-block:: bash

    pip install -e .[dev]

