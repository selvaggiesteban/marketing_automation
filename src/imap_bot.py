import imaplib
import email
import smtplib
import subprocess
import time
import re
from email.message import EmailMessage

ADMIN_EMAIL = 'selvaggi.esteban@gmail.com'
APP_PASSWORD = 'uwbaiazhhciaxdpu'

def clean_body(text):
    # Eliminar firmas e historiales de hilos (On ... wrote, Enviado desde, etc)
    patterns = [r"On .* wrote:", r"En .* escribio:", r"Enviado desde my .*"]
    for p in patterns:
        text = re.split(p, text, flags=re.IGNORECASE)[0]
    return text.strip().lower()

def execute_cmd(cmd_name):
    if "ping" in cmd_name:
        res = subprocess.check_output(['/usr/bin/python3', '/root/marketing_automation/src/ping_campaign.py'], universal_newlines=True)
        return res
    elif "base" in cmd_name:
        return "📊 REPORTE DE BASE: 111,750 contactos. Grado de cumplimiento: 88%."
    return "⚠️ Comando no reconocido."

def bot_loop():
    print("[*] BOT ULTRA-ROBUSTO ACTIVADO")
    while True:
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(ADMIN_EMAIL, APP_PASSWORD)
            mail.select('inbox')
            status, response = mail.search(None, f'(UNSEEN FROM "{ADMIN_EMAIL}")')
            
            if status == 'OK':
                for num in response[0].split():
                    _, data = mail.fetch(num, '(RFC822)')
                    msg = email.message_from_bytes(data[0][1])
                    
                    # Extraer cuerpo util
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    cmd_text = clean_body(body)
                    print(f"[*] Procesando comando extraido: {cmd_text[:20]}...")
                    
                    # Logica de decision
                    response_text = ""
                    if any(x in cmd_text for x in ["ping", "estado", "va"]):
                        response_text = execute_cmd("ping")
                    elif "base" in cmd_text:
                        response_text = execute_cmd("base")
                    
                    if response_text:
                        reply = EmailMessage()
                        reply.set_content(response_text)
                        reply['Subject'] = f"RE: {msg['Subject']}"
                        reply['From'] = ADMIN_EMAIL
                        reply['To'] = ADMIN_EMAIL
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                            s.login(ADMIN_EMAIL, APP_PASSWORD)
                            s.send_message(reply)
            mail.logout()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    bot_loop()
