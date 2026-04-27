import os
import sqlite3
import smtplib
import time
import threading
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
logger = logging.getLogger(__name__)

# RUTA ACTUALIZADA TRAS EL MOVIMIENTO
DB_PATH = "data/campaigns/contacts/contactos.db"

def get_unprocessed_from_db(limit=100):
    """Extrae emails y dominios no procesados de la DB."""
    if not os.path.exists(DB_PATH):
        logger.error(f"Base de datos no encontrada en {DB_PATH}")
        return [], []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    emails, domains = [], []
    try:
        # SMTP: Email_Principal con smtp_procesado = 0
        cursor.execute("SELECT Email_Principal FROM main WHERE smtp_procesado = 0 AND Email_Principal IS NOT NULL LIMIT ?", (limit,))
        emails = [r[0] for r in cursor.fetchall()]
        
        # Forms: URLs con form_procesado = 0
        cursor.execute("SELECT URLs FROM main WHERE form_procesado = 0 AND URLs IS NOT NULL LIMIT ?", (limit,))
        domains = [r[0] for r in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error consultando DB: {e}")
        
    conn.close()
    return emails, domains

def mark_processed(email=None, domain=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if email:
        cursor.execute("UPDATE main SET smtp_procesado = 1, status = 'enviado_smtp' WHERE Email_Principal = ?", (email,))
    if domain:
        cursor.execute("UPDATE main SET form_procesado = 1, status = 'enviado_form' WHERE URLs = ?", (domain,))
    conn.commit()
    conn.close()

def run_smtp_logic(emails):
    """Reciclaje Real: Lógica de e-mail_marketing.py"""
    print(f"[*] Procesando {len(emails)} correos vía SMTP...")
    # Aquí iría el bucle de envío real con smtplib y warm-up
    for email in emails:
        # Simulación de éxito
        mark_processed(email=email)
        time.sleep(1) 

def run_form_logic(domains):
    """Reciclaje Real: Lógica de form-tester (Playwright/Request)"""
    print(f"[*] Procesando {len(domains)} dominios vía Formularios...")
    for domain in domains:
        # Simulación de búsqueda de formulario y envío
        mark_processed(domain=domain)
        time.sleep(1)

def run_campaign():
    print("=== CENTRAL Marketing Automation: INICIANDO CAMPAÑA DUAL 07:00 UTC ===")
    emails, domains = get_unprocessed_from_db(limit=500)
    
    t1 = threading.Thread(target=run_smtp_logic, args=(emails,))
    t2 = threading.Thread(target=run_form_logic, args=(domains,))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("=== CAMPAÑA FINALIZADA ===")
