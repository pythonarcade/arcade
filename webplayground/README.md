# Arcade Web Testing
This directory contains a utility for early testing of Arcade in web browsers.

An http server is provided with the `server.py` file. This file can be run with `python server.py` and will serve a local HTTP server on port 8000.

The index page will provide a list of all Arcade examples. This is generated dynamically on the fly when the page is loaded, and will show all examples in the `arcade.examples` package. This generates links which can be followed to open any example in the browser.

## Testing Local Scripts

You can now test your own local scripts **without restarting the server**!

1. Navigate to `http://localhost:8000/local` in your browser
2. Place your Python scripts in the `local_scripts/` directory
3. Scripts should have a `main()` function as the entry point
4. The page will automatically list all `.py` files in that directory
5. Click any script to run it in the browser
6. Edit your scripts and refresh the browser page to see changes - no server restart needed!

See `local_scripts/README.md` and `local_scripts/example_test.py` for more details and examples.

## Prerequisites

You will need to have `uv` installed to build the Arcade wheel. You can install it with:

When you start the server, it will automatically build an Arcade wheel and copy it into this directory. 
This means that if you make any changes to Arcade code, you will need to restart the server to build a new wheel with your changes.

## How does this work?

The web server itself is built with a nice little HTTP server library named [Bottle](https://github.com/bottlepy/bottle). We need to run an HTTP server locally
to load anything into WASM in the browser, as it will not work if we just serve files directly due to browser security constraints. For the Arcade examples specifically,
we are taking advantage of the fact that the example code is packaged directly inside of Arcade to enable executing them in the browser.

If we need to add extra code that is not part of the Arcade package, that will require extension of this server to handle packaging it properly for loading into WASM, and then
serving that package.