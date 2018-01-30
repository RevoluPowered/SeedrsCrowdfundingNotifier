import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "os",
        "idna",
        "multiprocessing",
        "pyttsx3.drivers.sapi5",
        "win32com.client",
        "win32api",
        "plyer"
    ],
    "include_files" : [
        "notification.ico",
        "notification_sound.mp3"
    ],
    "include_msvcr":True
}

setup(
    name = "Yatter Seedrs Notifier",
    version = "0.1",
    description = "A notification tool for the seedrs platform",
    options = {"build_exe": build_exe_options},
    executables = [Executable("YatterNotifier.py")])