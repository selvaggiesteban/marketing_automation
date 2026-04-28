import os
import threading
import subprocess

def run_smtp_test():
    print('[*] Iniciando Motor SMTP de Excelencia...')
    # Usamos el venv para asegurar que las dependencias esten presentes
    subprocess.run(['/root/marketing_automation/venv/bin/python', 'src/email_marketing.py'])

def run_web_test():
    print('[*] Iniciando Motor Web Form de Excelencia...')
    # Procesamos los dominios solicitados
    subprocess.run(['/root/marketing_automation/venv/bin/python', 'src/form_processor.py', 'process', '--domain', 'selvaggiesteban.dev'])
    subprocess.run(['/root/marketing_automation/venv/bin/python', 'src/form_processor.py', 'process', '--domain', 'lanuscomputacion.com'])

if __name__ == '__main__':
    print('=== ORQUESTADOR CENTRAL: INICIANDO PRUEBA DUAL TOTAL ===')
    # Sincronizamos los hilos para que corran en paralelo
    t1 = threading.Thread(target=run_smtp_test)
    t2 = threading.Thread(target=run_web_test)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    print('=== PRUEBA DUAL FINALIZADA ===')
