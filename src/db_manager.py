import sqlite3
from datetime import datetime

DB_PATH = '/root/marketing_automation/data/campaigns/contacts/contactos.db'

def update_email_status(email, success, response):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    status = 1 if success else 0
    try:
        cursor.execute('UPDATE main SET smtp_procesado = ?, email_last_response = ? WHERE Email_Principal = ?', (status, response, email))
        conn.commit()
        print(f'[DB] Email {email} -> {status}')
    except Exception as e:
        print(f'[DB-ERROR] {e}')
    finally:
        conn.close()

def update_form_status(domain, success, response):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    status = 1 if success else 0
    try:
        cursor.execute('UPDATE main SET form_procesado = ?, form_last_response = ?, last_validation_date = ? WHERE URLs LIKE ?', (status, response, datetime.now().isoformat(), f'%{domain}%'))
        conn.commit()
        print(f'[DB] Dominio {domain} -> {status}')
    except Exception as e:
        print(f'[DB-ERROR] {e}')
    finally:
        conn.close()
