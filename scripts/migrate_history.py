import csv
import sqlite3
import os
from datetime import datetime

# Nueva fuente de verdad solicitada
CSV_ENRICHED = r"C:\Users\Esteban Selvaggi\Desktop\Diseño web\campaigns_reports\detailed_sent_report_enriched.csv"
DB_PATH = r"C:\Users\Esteban Selvaggi\Desktop\Diseño web\marketing_automation\logs\marketing_memory.db"

def migrate_from_enriched():
    if not os.path.exists(CSV_ENRICHED):
        print(f"[-] No se encontró el archivo enriquecido en {CSV_ENRICHED}")
        return

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            subject TEXT,
            message_path TEXT,
            contact_list_path TEXT,
            last_used DATETIME
        )
    ''')

    print(f"[*] Extrayendo historial desde: {os.path.basename(CSV_ENRICHED)}...")
    
    with open(CSV_ENRICHED, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        added_count = 0
        seen_campaigns = set()
        
        for row in reader:
            subject = row['Asunto']
            # Para el historial, usamos el Asunto como nombre si no hay otro
            name = f"Campaña: {subject}"
            
            # Nota: El reporte enriquecido no tiene el PATH del mensaje original, 
            # pero lo vinculamos al estándar para que sea seleccionable.
            msg_path = "campaigns/e-mail/message.md" 
            lst_path = CSV_ENRICHED # Usamos este mismo CSV como lista para re-contactar
            
            if subject not in seen_campaigns:
                cursor.execute('''
                    INSERT INTO campaigns (name, subject, message_path, contact_list_path, last_used)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, subject, msg_path, lst_path, row['Fecha']))
                seen_campaigns.add(subject)
                added_count += 1
    
    conn.commit()
    conn.close()
    print(f"[+] Migración exitosa. {added_count} campañas únicas detectadas y cargadas.")

if __name__ == "__main__":
    migrate_from_enriched()
