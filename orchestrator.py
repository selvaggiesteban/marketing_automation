import sqlite3
import subprocess
import threading
import os
import re
import sys
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# CONFIGURACION DE RUTAS SOBERANAS
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "contactos.db"
SRC_DIR = BASE_DIR / "src"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

def update_db(email, channel):
    """Persistencia atomica verificada."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        if channel == 'SMTP':
            cursor.execute('UPDATE main SET smtp_procesado=1, email_last_response=\"SMTP_OK\" WHERE Email_Principal=?', (email,))
        else:
            cursor.execute('UPDATE main SET form_procesado=1, form_last_response=\"FORM_OK\", last_validation_date=? WHERE URLs LIKE ?', (now, f'%{email}%'))
        conn.commit()
        conn.close()
        print(f'[CONCATENACION] {channel} {email} -> DB ACTUALIZADA')
    except Exception as e:
        print(f'[CRITICO] Error DB: {e}')

def run_smtp():
    """Motor SMTP con Interfaz Silenciosa y Codificacion UTF-8."""
    engine_dir = SRC_DIR / "e-mail_marketing"
    engine_path = engine_dir / "e-mail_marketing.py"
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tf_msg:
        tf_msg.write(os.getenv('MESSAGE_BODY', 'Mensaje soberano.'))
        temp_msg_path = tf_msg.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tf_list:
        tf_list.write(os.getenv('EMAIL_LIST', 'selvaggi.esteban@gmail.com'))
        temp_list_path = tf_list.name

    env = os.environ.copy()
    env['PYTHONPATH'] = str(engine_dir)
    env['PYTHONUTF8'] = '1'
    env['MESSAGE'] = temp_msg_path
    env['CONTACT_LIST'] = temp_list_path

    try:
        # Forzamos encoding='utf-8' en el Popen para Windows
        process = subprocess.Popen([sys.executable, str(engine_path)], 
                                   cwd=str(engine_dir), stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                   text=True, encoding='utf-8', env=env)
        stdout, _ = process.communicate(input='s\n')
        for line in stdout.splitlines():
            print(f'[SMTP] {line}')
            if '[EXITO]' in line:
                m = re.search(r'[\w\.-]+@[\w\.-]+', line)
                if m: update_db(m.group(0), 'SMTP')
    except Exception as e:
        print(f'[ERROR] SMTP: {e}')
    finally:
        for p in [temp_msg_path, temp_list_path]:
            if os.path.exists(p): os.remove(p)

def run_web():
    """Motor Web Form con Blindaje de Codificacion UTF-8."""
    engine_dir = SRC_DIR / "form-tester"
    main_script = engine_dir / "main.py"
    
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{engine_dir};{engine_dir / 'src'}"
    env['PYTHONUTF8'] = '1'
    
    try:
        domain = os.getenv('DOMAINS_LIST', 'selvaggiesteban.dev').split(',')[0]
        # Forzamos encoding='utf-8' para evitar el error de 'charmap'
        process = subprocess.Popen([sys.executable, str(main_script), "process", "--domain", domain], 
                                   cwd=str(engine_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                   text=True, encoding='utf-8', env=env)
        for line in process.stdout:
            print(f'[WEB] {line}', end='')
            if '[OK]' in line:
                update_db(domain, 'WEB')
        process.wait()
    except Exception as e:
        print(f'[ERROR] WEB: {e}')

if __name__ == '__main__':
    print('=== ORQUESTADOR SOBERANO v6.0 (UTF-8 REPAIRED) ===')
    t1 = threading.Thread(target=run_smtp)
    t2 = threading.Thread(target=run_web)
    t1.start(); t2.start(); t1.join(); t2.join()
    
    report_script = SRC_DIR / "utils" / "report_generator.py"
    if report_script.exists():
        print("[*] Generando Reporte de Excelencia...")
        subprocess.run([sys.executable, str(report_script)], env=os.environ.copy())
