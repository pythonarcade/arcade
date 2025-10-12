# Arcade Web Testing
This directory contains a utility for early testing of Arcade in web browsers.

An http server is provided with the `server.py` file. This file can be run with `python server.py` and will serve a local HTTP server on port 8000.

The index page will provide a list of all Arcade examples. This is generated dynamically on the fly when the page is loaded, and will show all examples in the `arcade.examples` package. This generates links which can be followed to open any example in the browser.

There are some pre-requesites to running this server. It assumes that you have the `development` branch of Pyglet 
checked out and in a folder named `pyglet` directly next to your Arcade repo directory. You will also need to have
the `build` and `flit` packages from PyPi installed. These are used by Pyglet and Arcade to build wheel files,
but are not generally installed for local development.

Assuming you have Pyglet ready to go, you can then start the server. It will build wheels for both Pyglet and Arcade, and copy them
into this directory. This means that if you make any, you will need to restart this server in order to build new wheels.

## How does this work?

The web server itself is built with a nice little HTTP server library named [Bottle](https://github.com/bottlepy/bottle). We need to run an HTTP server locally
to load anything into WASM in the browser, it will not work if we just server it files directly due to browser security constraints. For the Arcade examples specifically,
we are taking advantage of the fact that the example code is packaged directly inside of Arcade to enable executing them in the browser.

If we need to add extra code that is not part of the Arcade package, that will require extension of this server to handle packaging it properly for loading into WASM, and then
serving that package.