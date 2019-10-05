import site
import shutil
import os
import subprocess


python_root = site.getsitepackages()[0]

shutil.copyfile(f"{python_root}/Lib/site-packages/arcade/Win64/avbin.dll", "avbin.dll")
shutil.copyfile(f"avbin.dll", "avbin64.dll")
sp = subprocess.run(["pyinstaller",  "--exclude-module", "tkinter", "--add-data", "resources;resources", "--add-data",
                     "./avbin64.dll;.", "--add-data", "./avbin.dll;Win64", "--onefile", "--noconsole", "sample.py"],
                    stdout=subprocess.PIPE)
# rem pyinstaller --exclude-module tkinter --add-data resources;resources --add-data ./avbin64.dll;.
#                 --add-data ./avbin.dll;Win64 --onefile --noconsole sample.py
# print(sp.stdout)
os.unlink("avbin.dll")
os.unlink("avbin64.dll")

