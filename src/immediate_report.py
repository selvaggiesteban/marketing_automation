
import imaplib
import smtplib
from email.message import EmailMessage
import datetime

# Extraido de Gmail.txt
accounts = [
    ('selvaggiesteban4@gmail.com', 'brrzydkarigaqopi'),
    ('selvaggi.esteban@gmail.com', 'uwbaiazhhciaxdpu'),
    ('selvaggiesteban11@gmail.com', 'hphriqjrnsovyhvo'),
    ('marketing1a1oficial@gmail.com', 'atcdyuvlylzfezcj'),
    ('selvaggiconsultores@gmail.com', 'kfprymhzvtjtkecg'),
    ('estebanmfwd@gmail.com', 'knoazqvwrfukengs'),
    ('selvaggiesteban9@gmail.com', 'gxjqejkqrfiassvs')
]

def get_inbox_summary():
    summary = "=== REPORTE DE BANDEJA UNIFICADO (TEST INMEDIATO) ===\n"
    summary += f"Generado: {datetime.datetime.now().strftime('%H:%M:%S')} UTC\n\n"
    
    total_unread = 0
    senders = []

    for email, pwd in accounts:
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(email, pwd)
            mail.select('inbox')
            status, response = mail.search(None, 'UNSEEN')
            unread_count = len(response[0].split()) if response[0] else 0
            total_unread += unread_count
            summary += f"- {email}: {unread_count} no leídos.\n"
            mail.logout()
        except:
            summary += f"- {email}: ERROR DE CONEXION.\n"

    summary += f"\nTOTAL NO LEIDOS EN ECOSISTEMA: {total_unread}\n"
    summary += "\nNota: La base de datos de contactos NO ha sido modificada."
    return summary

def send_report():
    text = get_inbox_summary()
    msg = EmailMessage()
    msg.set_content(text)
    msg['Subject'] = '📊 REPORTE DE OPERACIONES 17:00 (EJECUCIÓN INMEDIATA)'
    msg['From'] = 'selvaggi.esteban@gmail.com'
    msg['To'] = 'selvaggi.esteban@gmail.com'
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login('selvaggi.esteban@gmail.com', 'uwbaiazhhciaxdpu')
        s.send_message(msg)
    print("[+] Reporte enviado.")

if __name__ == "__main__":
    send_report()
