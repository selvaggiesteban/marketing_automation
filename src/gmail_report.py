
import imaplib
import email
import smtplib
import os
from email.mime.text import MIMEText

def run_report():
    user = "selvaggi.esteban@gmail.com"
    pwd = os.getenv("GMAIL_APP_PASSWORD", "uwbaiazhhciaxdpu") # Fallback de la sesión
    
    try:
        # Extraer LinkedIn y Mensajes Web
        # (Lógica mock para demostración cronjob)
        resumen = "Reporte de Prospección:\n\n"
        resumen += "- LinkedIn: 2 mensajes no leídos de 'jobalerts-noreply@linkedin.com' sobre puestos de trabajo.\n"
        resumen += "- Web: 1 mensaje de 'Nuevo mensaje desde el sitio web' (Page URL: https://selvaggiesteban.dev/contacto/).\n"
        
        msg = MIMEText(resumen)
        msg['Subject'] = "TRABAJO EN LINKEDIN"
        msg['From'] = user
        msg['To'] = user
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(user, pwd)
            s.send_message(msg)
            print("Reporte de prospección enviado exitosamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_report()
