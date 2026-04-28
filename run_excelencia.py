import subprocess
import threading
import os
import re
import sqlite3
from datetime import datetime

DB_PATH = '/root/marketing_automation/data/campaigns/contacts/contactos.db'
log_file = 'unified_campaign.log'

def ensure_test_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM main WHERE Email_Principal = " selvaggi.esteban@gmail.com\')
 cursor.execute('INSERT INTO main (Email_Principal, URLs, smtp_procesado, form_procesado) VALUES (?, ?, 0, 0)', 
 ('selvaggi.esteban@gmail.com', 'https://selvaggiesteban.dev'))
 conn.commit()
 conn.close()
 print('[DB] Contactos de prueba inyectados para validacion de almacenamiento.')

def update_db(email, success, response, channel):
 conn = sqlite3.connect(DB_PATH)
 cursor = conn.cursor()
 status = 1 if success else 0
 if channel == 'SMTP':
 cursor.execute('UPDATE main SET smtp_procesado = ?, email_last_response = ? WHERE Email_Principal = ?', (status, response, email))
 else:
 cursor.execute('UPDATE main SET form_procesado = ?, form_last_response = ?, last_validation_date = ? WHERE URLs LIKE ?', (status, response, datetime.now().isoformat(), f'%{email}%'))
 conn.commit()
 conn.close()
 print(f'[CONCATENACION] {channel} {email} -> DB UPDATED')

def run_command(cmd, name, processor, cwd=None):
 with open(log_file, 'a') as f:
 f.write(f'\n--- {name} START [{datetime.now()}] ---\n')
 env = os.environ.copy()
 if 'form_tester_engine' in (cwd or ''):
 env['PYTHONPATH'] = '/root/marketing_automation/form_tester_engine:/root/marketing_automation/form_tester_engine/src'
 
 process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=cwd, env=env)
 for line in process.stdout:
 f.write(f'[{name}] {line}')
 print(f'[{name}] {line}', end='')
 # Procesamos cada linea para buscar eventos de exito y concatenarlos en la DB
 if '[EXITO]' in line:
 m = re.search(r'[\w\.-]+@[\w\.-]+', line)
 if m: update_db(m.group(0), True, 'SMTP_OK', 'SMTP')
 if '[OK]' in line and 'Formulario' in line:
 update_db('selvaggiesteban.dev', True, 'FORM_OK', 'WEB')
 process.wait()

if __name__ == '__main__':
 if os.path.exists(log_file): os.remove(log_file)
 ensure_test_data()
 print('=== INICIANDO ORQUESTACION DE EXCELENCIA DUAL ===')
 t1 = threading.Thread(target=run_command, args=(['/root/marketing_automation/venv/bin/python', 'src/email_marketing.py'], 'SMTP', None))
 t2 = threading.Thread(target=run_command, args=(['/root/marketing_automation/venv/bin/python', 'main.py', 'process', '--domain', 'selvaggiesteban.dev'], 'WEB', None, '/root/marketing_automation/form_tester_engine'))
 t1.start()
 t2.start()
 t1.join()
 t2.join()
 print(f'\n[!] PRUEBA FINALIZADA. LOG UNIFICADO: {log_file}')
