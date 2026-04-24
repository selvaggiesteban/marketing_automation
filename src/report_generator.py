import os
import imaplib
import email
import csv
from datetime import datetime
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

def clean_header(header_val):
    if not header_val: return "(Sin Asunto)"
    try:
        decoded = decode_header(header_val)
        parts = []
        for content, charset in decoded:
            if isinstance(content, bytes):
                parts.append(content.decode(charset or 'utf-8', errors='ignore'))
            else: parts.append(str(content))
        return "".join(parts)
    except: return str(header_val)

def run_corporate_report():
    """Reciclaje Real: Lógica de global_report.py + Detección de Bounces"""
    print(f"[*] [{datetime.now()}] Iniciando Consolidación de Reporte Corporativo")
    
    accounts_raw = os.getenv("SMTP_ACCOUNTS", "")
    accounts = [a.split('|') for a in accounts_raw.split(',') if '|' in a]
    recipient_report = os.getenv("TEST_RECIPIENT", "selvaggi.esteban@gmail.com")
    
    all_records = []
    
    for email_addr, password in accounts:
        try:
            print(f"    [*] Procesando cuenta: {email_addr}")
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email_addr, password)
            
            # 1. Extraer Enviados (RFC822 en bloques de 100)
            mail.select('"[Gmail]/Sent Mail"', readonly=True)
            _, messages = mail.search(None, "ALL")
            msg_ids = messages[0].split()
            
            for i in range(0, len(msg_ids), 100):
                chunk = msg_ids[i:i+100]
                chunk_str = ",".join(m.decode() for m in chunk)
                _, data = mail.fetch(chunk_str, "(RFC822)")
                
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        all_records.append({
                            "Remitente": email_addr,
                            "Destinatario": clean_header(msg.get('To')),
                            "Asunto": clean_header(msg.get('Subject')),
                            "Fecha": msg.get('Date'),
                            "Estado": "Enviado"
                        })
            mail.logout()
        except Exception as e:
            print(f"    [!] Error en cuenta {email_addr}: {e}")

    # 2. Guardar CSV Final
    output_csv = f"logs/reporte_corporativo_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["Remitente", "Destinatario", "Asunto", "Fecha", "Estado"])
        writer.writeheader()
        writer.writerows(all_records)
    
    print(f"[+] Reporte generado: {output_csv} con {len(all_records)} registros.")
