"""
Mock tkinter and PIL before importing stamp_collector so tests can run
without a display server.
"""
import sys
from unittest.mock import MagicMock

for _mod in [
    "tkinter",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.filedialog",
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",
]:
    sys.modules[_mod] = MagicMock()
