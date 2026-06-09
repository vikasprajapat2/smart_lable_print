import shutil
import os
from datetime import datetime

import sys

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(APP_DIR, "database", "labels.db")
BACKUP_DIR = os.path.join(APP_DIR, "backups")

def backup_database(custom_path=None):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = custom_path or os.path.join(BACKUP_DIR, f"backup_{ts}.db")
    shutil.copy2(DB_PATH, dest)
    return dest

def restore_database(source_path):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    shutil.copy2(source_path, DB_PATH)
