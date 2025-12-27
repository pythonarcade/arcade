# Local Scripts Directory

This directory is for testing your own Arcade scripts in the web environment without restarting the server.

## How to Use

1. Place your Python script (`.py` file) in this directory
2. Write your script using the standard `if __name__ == "__main__":` pattern (see example below)
3. Navigate to `http://localhost:8000/local` in your browser to see the list of available scripts
4. Click on any script to run it in the browser
5. Edit your script and refresh the browser page to see changes - **no server restart needed!**
   - Scripts are never cached, so refreshing always loads the latest version
   - No need for hard refresh (Ctrl+F5) - a simple refresh is enough

## Example Script Structure

```python
import arcade


class MyWindow(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "My Test")
        
    def on_draw(self):
        self.clear()
        # Your drawing code here
        arcade.draw_text(
            "Hello World!",
            self.width // 2,
            self.height // 2,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center"
        )


# Standard Python entry point - this will run when the script is loaded
if __name__ == "__main__":
    window = MyWindow()
    arcade.run()
```

**Note:** The `if __name__ == "__main__":` block is important! Your script's code will execute when loaded in the browser, just like running it normally with Python.

## Tips

- Scripts are loaded dynamically, so you can add, remove, or edit them while the server is running
- Just refresh the `/local` page to see newly added scripts
- Use the browser console (F12) to see any Python errors or debug output
- The example_test.py file shows a simple working example

## What Gets Loaded

- All `.py` files in this directory will appear in the local scripts list
- The web interface will load the Arcade wheel and execute your script
- When your script runs, the `if __name__ == "__main__":` block executes, just like running Python locally
- Pyodide environment is used to run Python in the browser

