import csv
import os
import time
import glob
import logging
from src.campaign_engine import send_email, get_delays
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def get_latest_report_path():
    """Busca el archivo de reporte enriquecido más reciente (Linux/VPS ready)."""
    search_paths = [
        "logs/detailed_sent_report_enriched*.csv",
        "reports/detailed_sent_report_enriched*.csv",
        "logs/reporte_corporativo_*.csv",
        "data/detailed_sent_report_enriched*.csv"
    ]
    
    all_files = []
    for pattern in search_paths:
        all_files.extend(glob.glob(pattern))
    
    if not all_files:
        return None
    
    # Retorna el archivo con la fecha de modificación más reciente
    return max(all_files, key=os.path.getmtime)

def run_targeted_remarketing(original_subject, new_subject, new_message_path):
    """
    REMARKETING REAL: Busca dinámicamente el ÚLTIMO reporte generado para mapear
    los remitentes originales y enviar el nuevo mensaje.
    """
    latest_csv = get_latest_report_path()
    
    if not latest_csv:
        print("[!] Error: No se encontró ningún reporte enriquecido para procesar.")
        return

    print(f"[*] Utilizando fuente de datos más reciente: {latest_csv}")
    
    if not os.path.exists(new_message_path):
        print(f"[!] Error: Mensaje no encontrado en {new_message_path}")
        return

    with open(new_message_path, 'r', encoding='utf-8') as f:
        new_body = f.read()

    # 1. Cargar mapeo Remitente -> Lista de Destinatarios
    print(f"[*] Analizando destinatarios para el asunto: '{original_subject}'...")
    sender_mapping = {}
    
    with open(latest_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Asunto'].strip().lower() == original_subject.strip().lower():
                if row['Estado'] == 'Entregado':
                    remitente = row['Remitente']
                    dest = row['Destinatario']
                    if remitente not in sender_mapping:
                        sender_mapping[remitente] = []
                    sender_mapping[remitente].append(dest)

    if not sender_mapping:
        print(f"[-] No se hallaron envíos exitosos bajo el asunto '{original_subject}' en el último reporte.")
        return

    # 2. Cargar credenciales
    accounts_raw = os.getenv("SMTP_ACCOUNTS", "")
    creds = {a.split('|')[0]: a.split('|')[1] for a in accounts_raw.split(',') if '|' in a}

    # 3. Envío Dirigido (Mismo remitente original + Warm-up)
    delay_gen = get_delays()
    total_envios = sum(len(v) for v in sender_mapping.values())
    print(f"[*] Iniciando Remarketing para {total_envios} contactos.")

    for sender_email, recipients in sender_mapping.items():
        if sender_email not in creds:
            print(f"[!] Sin credenciales para {sender_email}. Saltando.")
            continue
        
        print(f"\n[>] {sender_email} retomando hilo con {len(recipients)} contactos...")
        account_data = {"email": sender_email, "password": creds[sender_email]}
        
        for contact in recipients:
            success = send_email(account_data, contact, new_subject, new_body)
            logger.info(f"[{sender_email}] Remarketing a {contact}: {'EXITO' if success else 'FALLO'}")
            
            # Delay para proteger reputación
            delay = next(delay_gen)
            time.sleep(delay * 60)

    print("\n[+] Ciclo de remarketing dinámico completado.")
