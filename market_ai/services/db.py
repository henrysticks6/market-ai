import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("market_ai.db")

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT,
            description TEXT, location TEXT, contact TEXT, created_at TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT, business TEXT, category TEXT,
            offer TEXT, content TEXT, created_at TEXT)""")

def save_business(name, category, description, location="", contact=""):
    with connect() as con:
        con.execute("INSERT INTO businesses(name,category,description,location,contact,created_at) VALUES(?,?,?,?,?,?)",
                    (name,category,description,location,contact,datetime.now(timezone.utc).isoformat()))

def list_businesses():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM businesses ORDER BY id DESC").fetchall()]

def save_campaign(business, category, offer, content):
    with connect() as con:
        con.execute("INSERT INTO campaigns(business,category,offer,content,created_at) VALUES(?,?,?,?,?)",
                    (business,category,offer,content,datetime.now(timezone.utc).isoformat()))

def list_campaigns():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall()]
