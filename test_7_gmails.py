
import smtplib
from email.message import EmailMessage
import sqlite3
import os
from datetime import datetime

ADMIN_EMAIL = 'selvaggi.esteban@gmail.com'
APP_PASSWORD = 'uwbaiazhhciaxdpu'

target_emails = [
    'selvaggiesteban4@gmail.com', 'selvaggi.esteban@gmail.com', 'selvaggiesteban11@gmail.com',
    'marketing1a1oficial@gmail.com', 'selvaggiconsultores@gmail.com', 'wwwlanuscomputacion@gmail.com',
    'lanuscomputacioncom@gmail.com', 'estebanmfwd@gmail.com', 'esteselvaggi@hotmail.com',
    'selvaggi.esteban@icloud.com', 'selvaggiesteban9@gmail.com'
]

def run_test():
    print(f"[*] Iniciando prueba de fuego: Campaña a {len(target_emails)} cuentas conectadas...")
    
    # Simular DB
    conn = sqlite3.connect('/root/marketing_automation/test_db.sqlite')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS contacts (email TEXT, status TEXT)')
    for email in target_emails:
        c.execute('INSERT INTO contacts VALUES (?, ?)', (email, 'pending'))
    conn.commit()
    
    success_count = 0
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login(ADMIN_EMAIL, APP_PASSWORD)
        
        for email in target_emails:
            msg = EmailMessage()
            msg.set_content(f"Hola,\n\nEsta es una prueba automatizada del VPS (Motor SMTP).\nVerificando conectividad hacia la cuenta: {email}\n\nSaludos,\nComando Central.")
            msg['Subject'] = f"PRUEBA DE FLUJO SMTP - {datetime.now().strftime('%H:%M:%S')}"
            msg['From'] = ADMIN_EMAIL
            msg['To'] = email
            
            try:
                s.send_message(msg)
                c.execute("UPDATE contacts SET status='sent' WHERE email=?", (email,))
                success_count += 1
                print(f"[+] Enviado a: {email}")
            except Exception as e:
                print(f"[-] Fallo a {email}: {e}")
                
    conn.commit()
    conn.close()
    print(f"\n[=== PRUEBA COMPLETADA: {success_count}/{len(target_emails)} correos enviados ===]")

if __name__ == "__main__":
    run_test()
