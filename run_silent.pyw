import subprocess
import os

folder = os.path.dirname(os.path.abspath(_file_))
os.chdir(folder)

subprocess.Popen(
    [r"C:\Program Files\Python314\python3.14t.exe", "app.py"],
    creationflags=subprocess.CREATE_NO_WINDOW,
    cwd=folder
)