import shutil
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "labels.db")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")

def backup_database(custom_path=None):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = custom_path or os.path.join(BACKUP_DIR, f"backup_{ts}.db")
    shutil.copy2(DB_PATH, dest)
    return dest

def restore_database(source_path):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    shutil.copy2(source_path, DB_PATH)
