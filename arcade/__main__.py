import sys
import arcade


if __name__ == "__main__":
    window = arcade.Window()
    version_str = f"Arcade {arcade.__version__}"
    print()
    print(version_str)
    print('-' * len(version_str))
    print('vendor:', window.ctx.info.VENDOR)
    print('renderer:', window.ctx.info.RENDERER)
    print('version:', window.ctx.gl_version)
    print('python:', sys.version)
    print('platform:', sys.platform)
