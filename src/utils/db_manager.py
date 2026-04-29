import sqlite3
DB_PATH = '/root/marketing_automation/data/campaigns/contacts/contactos.db'

def get_next_targets(limit_email, limit_form):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Selección Inteligente: Contactos no procesados por SMTP
    cursor.execute('SELECT Email_Principal FROM main WHERE smtp_procesado = 0 AND Email_Principal IS NOT NULL LIMIT ?', (limit_email,))
    emails = [row[0] for row in cursor.fetchall()]
    # Selección Inteligente: Dominios no procesados por WEB
    cursor.execute('SELECT URLs FROM main WHERE form_procesado = 0 AND URLs IS NOT NULL LIMIT ?', (limit_form,))
    urls = [row[0] for row in cursor.fetchall()]
    conn.close()
    return emails, urls

def update_status(identifier, success, response, channel):
    conn = sqlite3.connect(DB_PATH)
    val = 1 if success else 0
    if channel == 'SMTP':
        conn.execute('UPDATE main SET smtp_procesado=?, email_last_response=? WHERE Email_Principal=?', (val, response, identifier))
    else:
        conn.execute('UPDATE main SET form_procesado=?, form_last_response=? WHERE URLs LIKE ?', (val, response, f'%{identifier}%'))
    conn.commit()
    conn.close()
