import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "data/contacts.db"
CSV_PATH = "logs/detailed_sent_report_enriched.csv"
ADMIN_EMAIL = os.getenv("TEST_RECIPIENT", "selvaggi.esteban@gmail.com")
SENDER_ACCOUNT = os.getenv("SMTP_ACCOUNTS", "").split(",")[0].split("|") if os.getenv("SMTP_ACCOUNTS") else ["", ""]

def run_corporate_report():
    """Genera y envía el reporte de las 17:00 UTC."""
    print(f"[*] [{datetime.now()}] Generando Reporte Corporativo Consolidado")
    
    if not os.path.exists(DB_PATH):
        print(f"[-] Archivo {DB_PATH} no encontrado.")
        return

    # Generar resumen del DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total, smtp_done, form_done = 0, 0, 0
    try:
        cursor.execute("SELECT COUNT(*) FROM main")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM main WHERE smtp_procesado = 1")
        smtp_done = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM main WHERE form_procesado = 1")
        form_done = cursor.fetchone()[0]
    except: pass
    conn.close()

    # Redactar cuerpo del correo
    body = f"""
=================================================
REPORTE CORPORATIVO DE CAMPAÑAS
=================================================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ESTADO DE LA BASE DE DATOS (contacts.db):
- Total de Contactos Registrados: {total}
- Procesados por SMTP (e-mail_marketing): {smtp_done}
- Procesados por Form-Tester: {form_done}

RESUMEN DE CAMPAÑA ACTUAL / ÚLTIMA:
- El sistema SMTP ha enviado a {smtp_done} correos.
- El sistema de Formularios ha contactado {form_done} dominios.

* Se adjunta copia física de contacts.db para resguardo local.
=================================================
"""
    
    # Enviar email con DB adjunta
    msg = MIMEMultipart()
    msg['From'] = SENDER_ACCOUNT[0]
    msg['To'] = ADMIN_EMAIL
    msg['Subject'] = f"REPORTE CORPORATIVO - {datetime.now().strftime('%d/%m/%Y')}"
    msg.attach(MIMEText(body, 'plain'))
    
    with open(DB_PATH, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=contacts.db")
        msg.attach(part)
        
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_ACCOUNT[0], SENDER_ACCOUNT[1])
            server.send_message(msg)
        print("[+] Reporte de las 17:00 UTC enviado exitosamente al administrador.")
    except Exception as e:
        print(f"[-] Error enviando el reporte: {e}")
