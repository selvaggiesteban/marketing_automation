import sqlite3, subprocess, threading, os, re
from datetime import datetime
DB_PATH = '/root/marketing_automation/data/campaigns/contacts/contactos.db'

def update_db(identifier, success, response, channel):
    conn = sqlite3.connect(DB_PATH)
    status = 1 if success else 0
    now = datetime.now().isoformat()
    try:
        if channel == 'SMTP':
            conn.execute('UPDATE main SET smtp_procesado = ?, email_last_response = ? WHERE Email_Principal = ?', (status, response, identifier))
        else:
            conn.execute('UPDATE main SET form_procesado = ?, form_last_response = ?, last_validation_date = ? WHERE URLs LIKE ?', (status, response, now, f'%{identifier}%'))
        conn.commit()
        print(f'[CONCATENACION] {channel} {identifier} -> OK')
    except Exception as e:
        print(f'[DB-ERROR] {e}')
    finally:
        conn.close()

def run_smtp():
    process = subprocess.Popen(['/root/marketing_automation/venv/bin/python', 'src/email_marketing.py'], 
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(f'[SMTP] {line}', end='')
        if '[EXITO]' in line:
            m = re.search(r'[\w\.-]+@[\w\.-]+', line)
            if m: update_db(m.group(0), True, 'SMTP_DELIVERED', 'SMTP')
    process.wait()

def run_web(domain):
    env = os.environ.copy()
    env['PYTHONPATH'] = '/root/marketing_automation/form_tester_engine:/root/marketing_automation/form_tester_engine/src'
    process = subprocess.Popen(['/root/marketing_automation/venv/bin/python', 'main.py', 'process', '--domain', domain], 
                               cwd='/root/marketing_automation/form_tester_engine', env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(f'[WEB] {line}', end='')
        if '[OK]' in line and 'Formulario' in line:
            update_db(domain, True, 'FORM_SUBMITTED', 'WEB')
    process.wait()

if __name__ == '__main__':
    print('=== ORQUESTADOR FINAL: PERSISTENCIA TOTAL ===')
    t1 = threading.Thread(target=run_smtp); t2 = threading.Thread(target=run_web, args=('selvaggiesteban.dev',))
    t1.start(); t2.start(); t1.join(); t2.join()
