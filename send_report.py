import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
load_dotenv('/root/marketing_automation/.env')
accounts = os.getenv('SMTP_ACCOUNTS').split(',')[0].split('|')
msg = MIMEMultipart()
msg['Subject'] = 'REPORTE FINAL EXCELENCIA - Campaña ID100'
msg['From'] = accounts[0]
msg['To'] = 'selvaggi.esteban@gmail.com'
msg.attach(MIMEText('Adjunto log unificado de SMTP y Formularios Web.', 'plain'))
with open('/root/marketing_automation/unified_campaign.log', 'rb') as f:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(f.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename=unified_campaign.log')
msg.attach(part)
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(accounts[0], accounts[1])
    server.send_message(msg)
