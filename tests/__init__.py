import os

# Headless mode
if os.environ.get("ARCADE_HEADLESS_TEST"):
    import pyglet
    pyglet.options.headless = True
