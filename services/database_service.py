import sys
import os
import json
import sqlite3
from datetime import datetime

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(APP_DIR, "database", "labels.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Active'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            line1 TEXT DEFAULT '',
            line2 TEXT DEFAULT '',
            line3 TEXT DEFAULT '',
            line4 TEXT DEFAULT '',
            font_size INTEGER DEFAULT 10,
            bold INTEGER DEFAULT 0,
            alignment TEXT DEFAULT 'center',
            printed INTEGER DEFAULT 0,
            printed_date DATETIME,
            line_styles TEXT DEFAULT '{}',
            FOREIGN KEY(sheet_id) REFERENCES sheets(id)
        )
    """)
    
    # Migration to add line_styles to existing database
    try:
        c.execute("ALTER TABLE labels ADD COLUMN line_styles TEXT DEFAULT '{}'")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    # Default settings
    defaults = [
        ("default_font_size", "10"),
        ("default_alignment", "center"),
        ("margin_top", "12.9"),
        ("margin_bottom", "12.9"),
        ("margin_left", "4.2"),
        ("margin_right", "4.2"),
        ("default_printer", ""),
    ]
    for k, v in defaults:
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()

# ─── Sheet operations ────────────────────────────────────────────────────────

def create_sheet(name):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO sheets (name, created_at, updated_at, status) VALUES (?, ?, ?, 'Active')", (name, now, now))
    sheet_id = c.lastrowid
    for pos in range(1, 17):
        c.execute("""INSERT INTO labels (sheet_id, position, line1, line2, line3, line4,
                     font_size, bold, alignment, printed, line_styles) VALUES (?,?,?,?,?,?,10,0,'center',0,'{}')""",
                  (sheet_id, pos, '', '', '', ''))
    conn.commit()
    conn.close()
    return sheet_id

def get_all_sheets():
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM sheets ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_sheets(query):
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute("""SELECT * FROM sheets WHERE name LIKE ? OR id LIKE ? OR
                        DATE(created_at) LIKE ? ORDER BY updated_at DESC""",
                     (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_sheet(sheet_id):
    conn = get_connection()
    c = conn.cursor()
    row = c.execute("SELECT * FROM sheets WHERE id=?", (sheet_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_sheet_timestamp(sheet_id):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE sheets SET updated_at=? WHERE id=?", (now, sheet_id))
    conn.commit()
    conn.close()

def delete_sheet(sheet_id):
    conn = get_connection()
    conn.execute("DELETE FROM labels WHERE sheet_id=?", (sheet_id,))
    conn.execute("DELETE FROM sheets WHERE id=?", (sheet_id,))
    conn.commit()
    conn.close()

# ─── Label operations ─────────────────────────────────────────────────────────

def get_labels(sheet_id):
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM labels WHERE sheet_id=? ORDER BY position", (sheet_id,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        # Parse line_styles
        try:
            d["line_styles_dict"] = json.loads(d.get("line_styles", "{}"))
        except:
            d["line_styles_dict"] = {}
        result.append(d)
    return result

def save_label(sheet_id, position, line1, line2, line3, line4, font_size, bold, alignment, line_styles=None):
    if line_styles is None:
        line_styles = {}
        
    conn = get_connection()
    conn.execute("""UPDATE labels SET line1=?, line2=?, line3=?, line4=?,
                    font_size=?, bold=?, alignment=?, line_styles=?
                    WHERE sheet_id=? AND position=?""",
                 (line1, line2, line3, line4, font_size, bold, alignment, json.dumps(line_styles), sheet_id, position))
    conn.commit()
    conn.close()
    update_sheet_timestamp(sheet_id)

def mark_printed(sheet_id, position):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("UPDATE labels SET printed=1, printed_date=? WHERE sheet_id=? AND position=?",
                 (now, sheet_id, position))
    conn.commit()
    conn.close()

def is_printed(sheet_id, position):
    conn = get_connection()
    c = conn.cursor()
    row = c.execute("SELECT printed FROM labels WHERE sheet_id=? AND position=?", (sheet_id, position)).fetchone()
    conn.close()
    return bool(row and row["printed"])

# ─── Settings ─────────────────────────────────────────────────────────────────

def get_setting(key, default=""):
    conn = get_connection()
    c = conn.cursor()
    row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key, value):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()
