import argparse
import sys
import os
from datetime import datetime
from src.campaign_engine import run_campaign
from src.report_generator import run_corporate_report
from src.backup_manager import run_backup
from src.memory_manager import list_history, get_campaign_by_id, save_to_memory
from src.remarketing_engine import run_targeted_remarketing
from src.imap_bot import listen_imap, run_sanitizer, fix_integrity

LOCK_FILE = "campaign.lock"

def main():
    parser = argparse.ArgumentParser(description="CENTRAL DE COMANDO Marketing Automation - SELVAGGIESTEBAN.DEV")
    parser.add_argument("--task", choices=["campaign", "report", "backup", "history", "remarketing", "listen", "sanitize", "fix"], required=True)
    
    # Parámetros (si aplican a opciones manuales o menú)
    parser.add_argument("--from_subject", type=str)
    parser.add_argument("--new_subject", type=str)
    parser.add_argument("--new_message", type=str)
    parser.add_argument("--load", type=int)
    parser.add_argument("--force", action="store_true")
    
    args = parser.parse_args()

    if args.task == "history":
        list_history()
    
    elif args.task == "remarketing":
        run_targeted_remarketing(args.from_subject, args.new_subject, args.new_message)

    elif args.task == "campaign":
        # Ahora campaign invoca SMTP y Form Tester
        run_campaign()
    
    elif args.task == "report":
        # Reporte corporativo de 17:00 UTC (adjunta DB y resumen dual)
        run_corporate_report()
    
    elif args.task == "backup":
        # 00:00 UTC: Local mirror + GDrive + Contraste DB
        run_backup()
        
    elif args.task == "listen":
        # Botón IMAP (lee tu email para las opciones 1-5)
        listen_imap()
        
    elif args.task == "sanitize":
        # Tanda de limpieza 100 en 100
        run_sanitizer()
        
    elif args.task == "fix":
        # Opción 5: Fix integridad
        fix_integrity()

if __name__ == "__main__":
    main()
