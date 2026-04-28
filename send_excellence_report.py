import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv('/root/marketing_automation/.env')

def send():
    recipient = 'selvaggi.esteban@gmail.com'
    accounts = os.getenv('SMTP_ACCOUNTS').split(',')[0].split('|')
    log_path = '/root/marketing_automation/unified_campaign.log'
    
    msg = MIMEMultipart()
    msg['Subject'] = 'REPORTE FINAL EXCELENCIA - Campaña ID100'
    msg['From'] = accounts[0]
    msg['To'] = recipient

    body = 'Adjunto log unificado de SMTP y Formularios Web. Ingenieria de Excelencia validada.'
    msg.attach(MIMEText(body, 'plain'))

    if os.path.exists(log_path):
        with open(log_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename=unified_campaign.log')
        msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(accounts[0], accounts[1])
        server.send_message(msg)
        print('OK')

if __name__ == '__main__':
    send()
EOF && /root/marketing_automation/venv/bin/python /root/marketing_automation/send_excellence_report.py
