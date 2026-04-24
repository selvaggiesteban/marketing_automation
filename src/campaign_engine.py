import sqlite3
import os
import smtplib
import time
import threading
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DB_PATH = "data/contacts.db"

def get_unprocessed_from_db(limit=500):
    """Extrae emails y dominios no procesados de la DB."""
    if not os.path.exists(DB_PATH):
        return [], []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Suponemos columnas: email, dominio, smtp_procesado, form_procesado
    try:
        cursor.execute("SELECT email FROM main WHERE smtp_procesado = 0 LIMIT ?", (limit,))
        emails = [r[0] for r in cursor.fetchall() if r[0]]
        
        cursor.execute("SELECT urls FROM main WHERE form_procesado = 0 LIMIT ?", (limit,))
        domains = [r[0] for r in cursor.fetchall() if r[0]]
    except Exception as e:
        logger.error(f"Error leyendo DB: {e}")
        emails, domains = [], []
        
    conn.close()
    return emails, domains

def mark_as_processed(email=None, domain=None):
    if not os.path.exists(DB_PATH): return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if email:
        cursor.execute("UPDATE main SET smtp_procesado = 1 WHERE email = ?", (email,))
    if domain:
        cursor.execute("UPDATE main SET form_procesado = 1 WHERE urls = ?", (domain,))
    conn.commit()
    conn.close()

def run_smtp_campaign(emails):
    print(f"[*] Iniciando envíos SMTP para {len(emails)} contactos...")
    # Aquí se integra la lógica de rotación y envío de e-mail_marketing.py
    # Simularemos la marcación para el flujo
    for e in emails:
        mark_as_processed(email=e)
        time.sleep(0.5) # Warm-up simplificado para el ejemplo

def run_form_tester_campaign(domains):
    print(f"[*] Iniciando envío por Formularios (Form-Tester) para {len(domains)} dominios...")
    # Integración con el motor de form-tester
    for d in domains:
        mark_as_processed(domain=d)
        time.sleep(0.5)

def run_campaign():
    """Ejecuta la campaña dual de las 07:00 UTC."""
    print("=== INICIANDO CAMPAÑA DUAL (SMTP + FORM TESTER) ===")
    emails, domains = get_unprocessed_from_db(limit=1000)
    
    t1 = threading.Thread(target=run_smtp_campaign, args=(emails,))
    t2 = threading.Thread(target=run_form_tester_campaign, args=(domains,))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("=== CAMPAÑA DUAL COMPLETADA ===")
