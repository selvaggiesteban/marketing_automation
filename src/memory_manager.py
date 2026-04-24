import sqlite3
import os
from datetime import datetime

DB_PATH = "logs/marketing_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            subject TEXT,
            message_path TEXT,
            contact_list_path TEXT,
            last_used DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def save_to_memory(name, subject, message_path, list_path):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO campaigns (name, subject, message_path, contact_list_path, last_used)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, subject, message_path, list_path, datetime.now()))
    conn.commit()
    conn.close()
    print(f"[+] Campaña '{name}' guardada en la memoria.")

def list_history():
    if not os.path.exists(DB_PATH):
        print("[-] No hay historial de campañas aún.")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, subject, last_used FROM campaigns ORDER BY last_used DESC")
    rows = cursor.fetchall()
    print("\n📜 HISTORIAL DE CAMPAÑAS SELECCIONABLES:")
    print(f"{'ID':<4} {'NOMBRE':<20} {'ASUNTO':<30} {'ÚLTIMO USO'}")
    print("-" * 75)
    for r in rows:
        print(f"{r[0]:<4} {r[1]:<20} {r[2]:<30} {r[3]}")
    conn.close()

def get_campaign_by_id(campaign_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT subject, message_path, contact_list_path FROM campaigns WHERE id = ?", (campaign_id,))
    res = cursor.fetchone()
    conn.close()
    return res
