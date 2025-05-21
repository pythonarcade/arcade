# Arcade Web Testing
This directory contains a utility and some examples for early Testing of Arcade in web browsers.

An http server is provided with the `server.py` file. This file can be run with `python server.py` and will serve
a local HTTP server on port 8000. From there, any desired example can be accessed in the browser by simply navigating
to it's path. For example to view the `basic_renderer` example, you would navigate to `http://localhost:8000/basic_renderer`.

There are some pre-requesites to running this server. It assums that you have [this branch](https://github.com/caffeinepills/pyglet/tree/pygodide)
of Pyglet checked out and in a folder named `pyglet` directly next to your Arcade repo directory. You will also need to have
the `build` and `flit` packages from PyPi installed. These are used by Pyglet and Arcade to build wheel files, but are not
generally installed for local development.

Assuming you have Pyglet ready to go, you can then start the server. It will build wheels for both Pyglet and Arcade, and copy them
into this directory. This means that if you make changes to Arcade or Pyglet, you will need to restart this server in order to
build new wheels for those changes to take effect. If you only change example code within this directory, there is no need to
restart the server for it to take effect.

## How does this work?

One problem with deploying into the web, is that the code and assets need to be injected into the WASM virtual filesystem. This can
be easier said than done. The provided HTTP server has a special component to it, that when it receives a request ending in `.zip` it will
look for a folder name matching the filename of the .zip. It will then create a .zip from that folder, and serve the zip file back.

This means that in an HTML file, code for an example can be included by simple appending `.zip` to the path to the package and assuming
it exists. The server will create it dynamically. For a very basic example, see `basic_renderer` in this directory.