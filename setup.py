import sys
from cx_Freeze import setup, Executable
import os.path
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "os",
        "idna",
        "multiprocessing",
        "win32com.client",
        "win32api",
        "pywintypes",
        "plyer",
        "requests.compat",
        "urllib3",
        "pyttsx3",
        "pystray",
        "PIL",
        "MicImagePlugin"
    ],
    "include_files": [
        "notification.ico",
        "notification_sound.mp3",
        "config.json"
    ],
    "include_msvcr": True
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "Yatter Seedrs Notifier",
    version = "0.3",
    description = "Seedrs investment notification",
    options = {"build_exe": build_exe_options},
    executables = [Executable("YatterNotifier.py", icon='notification.ico', base=base)])