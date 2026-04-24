import sqlite3
import os

DB_PATH = "data/contacts.db"

def patch():
    if not os.path.exists(DB_PATH):
        print(f"[!] Warning: {DB_PATH} no encontrada. Sube el archivo para aplicar el parche.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("PRAGMA table_info(main)")
    cols = [r[1] for r in c.fetchall()]
    
    # Columnas necesarias para la armonía del sistema C3
    required = {
        'smtp_procesado': 'INTEGER DEFAULT 0',
        'form_procesado': 'INTEGER DEFAULT 0',
        'status': "TEXT DEFAULT 'pendiente'"
    }
    
    for col, dtype in required.items():
        if col not in cols:
            c.execute(f"ALTER TABLE main ADD COLUMN {col} {dtype}")
            print(f"[+] Columna '{col}' inyectada con éxito.")
            
    conn.commit()
    conn.close()
    print("[+] Sincronización de esquema DB completada.")

if __name__ == "__main__":
    patch()
