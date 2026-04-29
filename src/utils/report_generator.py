import os, smtplib, sqlite3, re, glob
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# CONFIGURACION DE RUTAS SOBERANAS (Pathlib para Excelencia)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "contactos.db"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

def send_master_report():
    log_p = BASE_DIR / "unified_campaign.log"
    log_content = ''
    if log_p.exists():
        with open(log_p, 'r', encoding='utf-8', errors='ignore') as f: log_content = f.read()

    # 1. Detalle por Usuario (Gmail)
    accounts_env = os.getenv('SMTP_ACCOUNTS')
    if not accounts_env:
        print("[ALERTA] No se encontraron cuentas en el .env")
        return

    accounts = accounts_env.split(',')
    stats_per_user = {}
    for acc in accounts:
        email = acc.split('|')[0]
        count = log_content.count(f'[{email}] [EXITO]')
        stats_per_user[email] = count

    # 2. Métricas de DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM main WHERE smtp_procesado=1')
    smtp_total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM main WHERE form_procesado=1')
    form_total = c.fetchone()[0]
    db_size = os.path.getsize(DB_PATH) / (1024*1024)
    conn.close()

    msg = MIMEMultipart()
    msg['Subject'] = 'Reporte de campaña de e-mail marketing ID100'
    msg['From'] = accounts[0].split('|')[0]
    msg['To'] = 'selvaggi.esteban@gmail.com'

    body = "==========================================\n"
    body += "   Reporte de campaña de e-mail marketing ID100\n"
    body += "==========================================\n"
    body += "Nombre: Prueba\n"
    body += "Estado: EJECUCION COMPLETADA\n\n"
    body += "USUARIOS ACTIVOS / DETALLE DE ENVIOS:\n"
    for user, qty in stats_per_user.items():
        body += f"- {user}: {qty} envios\n"
    body += "\nMETRICAS TOTALES:\n"
    body += f"Envios SMTP: {smtp_total}\n"
    body += f"Envios de formularios: {form_total}\n"
    body += f"Base de Datos: {db_size:.1f} MB\n\n"
    body += "Adjunto Log unificado y Reporte PDF profesional.\n"
    body += "==========================================\n"
    
    msg.attach(MIMEText(body, 'plain'))

    # Adjuntos
    if log_p.exists():
        with open(log_p, 'rb') as f:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(f.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', 'attachment; filename=unified_campaign.log')
            msg.attach(p)

    reports_dir = BASE_DIR / "reports"
    if reports_dir.exists():
        pdfs = list(reports_dir.glob('*.pdf'))
        if pdfs:
            latest_pdf = max(pdfs, key=os.path.getctime)
            with open(latest_pdf, 'rb') as f:
                p = MIMEBase('application', 'octet-stream')
                p.set_payload(f.read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', f'attachment; filename={latest_pdf.name}')
                msg.attach(p)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(accounts[0].split('|')[0], accounts[0].split('|')[1])
            s.send_message(msg)
        print('OK')
    except Exception as e:
        print(f"[ERROR] No se pudo enviar el reporte: {e}")

if __name__ == '__main__':
    send_master_report()
