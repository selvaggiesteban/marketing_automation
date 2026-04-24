import argparse
import sys
import os
from datetime import datetime
from src.campaign_engine import run_campaign
from src.report_generator import run_corporate_report
from src.backup_manager import run_backup

def main():
    parser = argparse.ArgumentParser(description="MARKETING AUTOMATION - SELVAGGIESTEBAN.DEV")
    parser.add_argument("--task", choices=["campaign", "report", "backup"], required=True, help="Tarea a ejecutar")
    args = parser.parse_args()

    log_file = f"logs/task_{args.task}_{datetime.now().strftime('%Y%m%d')}.log"
    
    print(f"[*] Iniciando tarea: {args.task} a las {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        if args.task == "campaign":
            run_campaign()
        elif args.task == "report":
            run_corporate_report()
        elif args.task == "backup":
            run_backup()
    except Exception as e:
        print(f"[!] ERROR CRÍTICO en {args.task}: {e}")
        # Aquí se dispararía la alerta roja por email en producción
        sys.exit(1)

if __name__ == "__main__":
    main()
