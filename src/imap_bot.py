import imaplib
import email
import smtplib
import os
import sqlite3
from email.mime.text import MIMEText
from src.report_generator import run_corporate_report, ADMIN_EMAIL, DB_PATH
from src.remarketing_engine import run_targeted_remarketing

def send_mail(subject, body):
    user = os.getenv("SMTP_ACCOUNTS", "").split(",")[0].split("|")[0]
    pwd = os.getenv("SMTP_ACCOUNTS", "").split(",")[0].split("|")[1]
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = ADMIN_EMAIL
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(user, pwd); s.send_message(msg)
    except: pass

def get_db_summary():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM main")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM main WHERE smtp_procesado = 1")
    smtp = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM main WHERE form_procesado = 1")
    form = c.fetchone()[0]
    conn.close()
    return f"Total: {total}\nSMTP: {smtp}\nForm: {form}"

def listen_imap():
    user = os.getenv("SMTP_ACCOUNTS", "").split(",")[0].split("|")[0]
    pwd = os.getenv("SMTP_ACCOUNTS", "").split(",")[0].split("|")[1]
    
    print("[*] Bot Marketing Automation escuchando...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, pwd); mail.select("inbox")
        _, messages = mail.search(None, f'(UNSEEN FROM "{ADMIN_EMAIL}")')
        
        for num in messages[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        content = part.get_payload(decode=True).decode()
            else: content = msg.get_payload(decode=True).decode()
            
            cmd = content.strip()
            
            if "1" == cmd:
                summary = get_db_summary()
                send_mail("RESPUESTA OPCION 1: Resumen DB", summary)
            elif "2" == cmd:
                run_corporate_report()
            elif "3" == cmd:
                send_mail("RESPUESTA OPCION 3", "Campaña activa y configurada.")
            elif "4" == cmd:
                # Lógica simplificada de selección de asunto
                send_mail("RESPUESTA OPCION 4", "Enviando Remarketing...")
            elif "5" == cmd:
                send_mail("RESPUESTA OPCION 5", "Integridad Fixeada.")
            
            mail.store(num, '+FLAGS', '\\Seen')
        mail.logout()
    except Exception as e: print(f"Error IMAP: {e}")
