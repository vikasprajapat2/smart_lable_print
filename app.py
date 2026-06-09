import sys
import os

# Ensure local imports work whether run as script or frozen EXE
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

from ui.dashboard import Dashboard

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()
