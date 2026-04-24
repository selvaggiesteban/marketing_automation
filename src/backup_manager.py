import os
import subprocess
from datetime import datetime

def run_backup():
    """
    Orquesta el backup espejo a Google Drive usando Rclone.
    Configura el remoto 'gdrive' en el VPS antes de usar.
    """
    print(f"[*] [{datetime.now()}] Iniciando Sincronización con Google Drive...")
    
    # Directorio raíz del proyecto en el VPS (ajustar según despliegue)
    root_dir = "/root/marketing_automation"
    remote_target = "gdrive:Backups/MarketingAutomation_VPS"
    
    try:
        # Comando rclone sync: Hace un espejo exacto (borra en destino lo que no está en origen)
        # --progress para ver avance, --verbose para logs
        result = subprocess.run([
            "rclone", "sync", root_dir, remote_target,
            "--exclude", "logs/**",
            "--exclude", "venv/**",
            "--exclude", ".git/**"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Backup completado exitosamente.")
        else:
            print(f"[-] Error en Rclone: {result.stderr}")
            raise Exception("Fallo en sincronización Rclone")
            
    except FileNotFoundError:
        print("[!] Rclone no está instalado. Por favor ejecuta setup_vps.sh primero.")
