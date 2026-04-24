import os
import time
import smtplib
import imaplib
import email
import json
import threading
import datetime
import sys
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF
from dotenv import load_dotenv

# CLON IDENTICO DE e-mail_marketing.py
load_dotenv()

CAMPAIGN_ID = os.getenv("CAMPAIGN_ID", datetime.datetime.now().strftime("%Y%m%d"))
SUBJECT = os.getenv("SUBJECT", "Sin Asunto")
CONTACT_LIST_PATH = os.getenv("CONTACT_LIST", "contacts.txt")
MESSAGE_PATH = os.getenv("MESSAGE", "message.md")
TEST_RECIPIENT = os.getenv("TEST_RECIPIENT", "selvaggi.esteban@gmail.com")
SMTP_ACCOUNTS_RAW = os.getenv("SMTP_ACCOUNTS", "")
REPORT_DIRECTORY = "logs"

# Restauración de BOUNCE_KEYWORDS original
BOUNCE_KEYWORDS = [
    "Address not found", "The email account that you tried to reach does not exist",
    "Delivery Status Notification (Failure)", "Recipient address rejected",
    "Mail delivery failed", "mailbox unavailable", "permanent failure", "undeliverable",
    "Dirección no encontrada", "La cuenta de correo electrónico a la que intentaste llegar no existe",
    "Notificación de estado de entrega (error)", "Dirección del destinatario rechazada",
    "Fallo en la entrega del correo", "Buzón no disponible", "Fallo permanente",
    "No se pudo entregar", "El mensaje no se pudo entregar", "Cuenta de correo no válida"
]

stats = {
    "enviadas": 0, "entregados": 0, "errores": 0, "rebotes": 0,
    "total_contactos": 0, "estado": "Iniciando",
    "inicio_campana": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "fin_campana": "N/A"
}
stats_lock = threading.Lock()

def get_delays():
    cycle = list(range(1, 11)) + list(range(9, 1, -1))
    while True:
        for d in cycle: yield d

def send_email(account, recipient, subject, body, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = account['email']; msg['To'] = recipient; msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEBase("application", "octet-stream"); part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(attachment_path)}")
            msg.attach(part)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(account['email'], account['password'])
            server.send_message(msg)
        return True
    except Exception: return False

def worker(account, contacts, campaign_message):
    global stats
    delay_gen = get_delays()
    for contact in contacts:
        contact = contact.strip()
        if not contact: continue
        success = send_email(account, contact, SUBJECT, campaign_message)
        with stats_lock:
            stats["enviadas"] += 1
            if success: stats["entregados"] += 1
            else: stats["errores"] += 1
        if contact != contacts[-1]:
            delay = next(delay_gen)
            time.sleep(delay * 60)

def run_campaign():
    # Aquí se dispara la lógica idéntica de chunking y threading
    accounts = []
    if SMTP_ACCOUNTS_RAW:
        for acc in SMTP_ACCOUNTS_RAW.split(","):
            if "|" in acc:
                e, p = acc.split("|"); accounts.append({"email": e, "password": p})
    
    with open(MESSAGE_PATH, 'r', encoding='utf-8') as f: campaign_message = f.read()
    with open(CONTACT_LIST_PATH, 'r', encoding='utf-8') as f: all_contacts = [l.strip() for l in f if l.strip()]
    stats["total_contactos"] = len(all_contacts)
    
    num_accounts = len(accounts)
    chunk_size = (len(all_contacts) + num_accounts - 1) // num_accounts
    contact_chunks = [all_contacts[i:i + chunk_size] for i in range(0, len(all_contacts), chunk_size)]
    
    stats["estado"] = "En progreso"
    threads = []
    for i in range(num_accounts):
        if i < len(contact_chunks):
            t = threading.Thread(target=worker, args=(accounts[i], contact_chunks[i], campaign_message))
            t.start(); threads.append(t)
    for t in threads: t.join()
    stats["estado"] = "Completada"
