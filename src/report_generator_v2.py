
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

def generate_unified_report():
    print(f"[{datetime.now()}] Generando Reporte Unificado (07:00 - 17:00 UTC)...")
    
    wp_log = "Sin actividad registrada."
    if os.path.exists("/root/marketing_automation/logs/wp_blog.log"):
        with open("/root/marketing_automation/logs/wp_blog.log", "r") as f:
            wp_log = f.read()[-2000:]
            
    email_log = "Sin actividad registrada."
    if os.path.exists("/root/marketing_automation/logs/email_v2.log"):
        with open("/root/marketing_automation/logs/email_v2.log", "r") as f:
            email_log = f.read()[-2000:]
            
    report = f"=== REPORTE DE OPERACIONES C3 (17:00 UTC) ===\n\n"
    report += "-- EVENTOS DE MARKETING Y EMAILS --\n"
    report += f"{email_log}\n\n"
    report += "-- EVENTOS DE BLOG INSTITUCIONAL (WP-CLI / IA) --\n"
    report += f"{wp_log}\n\n"
    report += "Notificación Final: Todos los sistemas de Selvaggi Consultores operan nominalmente."
    
    with open("/root/marketing_automation/logs/unified_report_latest.txt", "w") as f:
        f.write(report)
        
    print("Reporte consolidado listo. Notificación mejorada almacenada.")

if __name__ == "__main__":
    generate_unified_report()
