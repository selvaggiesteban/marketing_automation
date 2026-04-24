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
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración técnica de SELVAGGIESTEBAN.DEV
CAMPAIGN_ID = os.getenv("CAMPAIGN_ID", datetime.datetime.now().strftime("%Y%m%d"))
SUBJECT = os.getenv("SUBJECT", "Sin Asunto")
CONTACT_LIST_PATH = os.getenv("CONTACT_LIST", "contacts.txt")
MESSAGE_PATH = os.getenv("MESSAGE", "message.md")
TEST_RECIPIENT = os.getenv("TEST_RECIPIENT", "selvaggi.esteban@gmail.com")
SMTP_ACCOUNTS_RAW = os.getenv("SMTP_ACCOUNTS", "")

# Logging blindado para VPS
log_path = f"logs/campaign_{CAMPAIGN_ID}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(log_path, encoding='utf-8'), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Lógica de Warm-Up (1-10 min)
def get_delays():
    cycle = list(range(1, 11)) + list(range(9, 1, -1))
    while True:
        for d in cycle:
            yield d

def send_email(account, recipient, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = account['email']
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(account['email'], account['password'])
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Error desde {account['email']} a {recipient}: {e}")
        return False

def worker(account, contacts, message):
    delay_gen = get_delays()
    for contact in contacts:
        contact = contact.strip()
        if not contact: continue
        
        success = send_email(account, contact, SUBJECT, message)
        status = "EXITO" if success else "FALLO"
        
        # Reporte de estado cada 5 minutos (implícito en el delay)
        if contact != contacts[-1]:
            delay = next(delay_gen)
            logger.info(f"[{account['email']}] [{status}] -> {contact}. Espera: {delay} min.")
            time.sleep(delay * 60)

def run_campaign():
    """Ejecuta el ciclo completo de campaña con alternancia y warm-up."""
    logger.info("=== INICIANDO MOTOR DE CAMPAÑA SELVAGGIESTEBAN.DEV ===")
    
    # 1. Cargar Cuentas
    accounts = []
    for acc in SMTP_ACCOUNTS_RAW.split(","):
        if "|" in acc:
            email_addr, password = acc.split("|")
            accounts.append({"email": email_addr, "password": password})
    
    if not accounts:
        logger.error("No hay cuentas configuradas en SMTP_ACCOUNTS.")
        return

    # 2. Cargar Mensaje y Contactos
    try:
        with open(MESSAGE_PATH, 'r', encoding='utf-8') as f:
            message = f.read()
        with open(CONTACT_LIST_PATH, 'r', encoding='utf-8') as f:
            contacts = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Error cargando archivos: {e}")
        return

    # 3. Distribución (Alternancia)
    num_accounts = len(accounts)
    chunk_size = (len(contacts) + num_accounts - 1) // num_accounts
    chunks = [contacts[i:i + chunk_size] for i in range(0, len(contacts), chunk_size)]

    logger.info(f"Distribuyendo {len(contacts)} contactos entre {num_accounts} cuentas.")

    threads = []
    for i in range(num_accounts):
        if i < len(chunks):
            t = threading.Thread(target=worker, args=(accounts[i], chunks[i], message))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    logger.info("=== CAMPAÑA FINALIZADA ===")
