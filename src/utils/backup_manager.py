import os
import subprocess
import shutil
from datetime import datetime
from src.report_generator import SENDER_ACCOUNT, ADMIN_EMAIL, DB_PATH
import smtplib
from email.mime.text import MIMEText
import sqlite3
import csv

def run_contrast():
    print("[*] Iniciando Fix de Integridad (00:00 UTC)...")
    csv_path = "logs/detailed_sent_report_enriched.csv"
    if not os.path.exists(csv_path) or not os.path.exists(DB_PATH):
        return

    # Contraste SMTP report vs DB (Igual que contrast_db_csv.py)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT email FROM main")
    db_emails = {r[0] for r in c.fetchall()}
    conn.close()

    csv_emails = set()
    csv_bounced = set()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            csv_emails.add(r['Destinatario'])
            if r['Estado'] == 'Rebotado':
                csv_bounced.add(r['Destinatario'])

    diferencias = len(csv_emails - db_emails)
    rebotes = len(db_emails.intersection(csv_bounced))

    # Notificación de integridad
    body = f"Integridad: {diferencias} correos en CSV no están en DB. {rebotes} correos en DB están rebotados. Por favor, corre el --task fix_integrity manual."
    msg = MIMEText(body)
    msg['From'] = SENDER_ACCOUNT[0]
    msg['To'] = ADMIN_EMAIL
    msg['Subject'] = "[ALERTA] Diferencias en DB vs CSV"
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_ACCOUNT[0], SENDER_ACCOUNT[1])
            server.send_message(msg)
    except: pass

def run_backup():
    """Backup a las 00:00 UTC: Local Overwrite + GDrive + Contraste DB."""
    print(f"[*] [{datetime.now()}] Iniciando Sincronización...")
    
    # 1. Contraste de Base de Datos
    run_contrast()
    
    root_dir = "/root/marketing_automation"
    local_backup_dir = "/root/marketing_automation_backup_mirror"
    remote_target = "gdrive:Backups/MarketingAutomation_VPS"
    
    # 2. Resguardo Local (Sobrescritura espejo / imagen)
    print(f"[*] Haciendo imagen local en {local_backup_dir}...")
    try:
        # Rclone sync local a local (o shutil.copytree con dirs_exist_ok=True en Python 3.8+)
        os.system(f"rsync -a --delete {root_dir}/ {local_backup_dir}/")
        print("[+] Imagen local sobrescrita y actualizada.")
    except Exception as e:
        print(f"[-] Error en backup local: {e}")
    
    # 3. Resguardo Remoto (GDrive)
    try:
        print("[*] Sincronizando con Google Drive...")
        subprocess.run([
            "rclone", "sync", root_dir, remote_target,
            "--exclude", "logs/**",
            "--exclude", "venv/**",
            "--exclude", ".git/**"
        ], capture_output=True, text=True)
        print("[+] Backup completado exitosamente.")
    except FileNotFoundError:
        print("[!] Rclone no está instalado.")
