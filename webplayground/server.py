#! /usr/bin/env python

import argparse
import http.server
import os
import shutil
import socketserver
import subprocess
from contextlib import contextmanager
from pathlib import Path

path_pyglet = Path("../../pyglet")
pyglet_wheel_filename = "pyglet-3.0.0a1-py3-none-any.whl"
path_pyglet_wheel = path_pyglet / "dist" / pyglet_wheel_filename

path_arcade = Path("../")
arcade_wheel_filename = "arcade-3.2.0-py3-none-any.whl"
path_arcade_wheel = path_arcade / "dist" / arcade_wheel_filename


class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def send_head(self):
        if self.path.endswith(".zip"):
            path = self.path
            if path.startswith("/"):
                path = Path("." + str(path)).resolve()

            shutil.make_archive(path.with_suffix(""), "zip", root_dir=path.parent)

        return super().send_head()


@contextmanager
def server(port):
    httpd = socketserver.TCPServer(("", port), HTTPHandler)
    httpd.allow_reuse_address = True
    try:
        yield httpd
    finally:
        httpd.shutdown()


def main():
    # Get us in this file's parent directory
    here = Path(__file__).parent.resolve()
    os.chdir(here)

    # Go to pyglet and build a wheel
    os.chdir(path_pyglet)
    subprocess.run(["python", "make.py", "dist"])
    os.chdir(here)
    shutil.copy(path_pyglet_wheel, f"./{pyglet_wheel_filename}")

    # Go to arcade and build a wheel
    os.chdir(path_arcade)
    subprocess.run(["python", "-m", "build", "--wheel", "--outdir", "dist"])
    os.chdir(here)
    shutil.copy(path_arcade_wheel, f"./{arcade_wheel_filename}")

    with server(8000) as httpd:
        print(f"Serving from {here} at http://localhost:8000")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
