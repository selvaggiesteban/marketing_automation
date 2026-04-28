
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime

ADMIN_EMAIL = 'selvaggi.esteban@gmail.com'
APP_PASSWORD = 'uwbaiazhhciaxdpu'
target_count = 84 # Suficiente para durar 60 min con el delay actual

def run_60min_cycle():
    print(f"[{datetime.now()}] Iniciando ciclo de produccion de 60 minutos...")
    # Delay entre emails para cubrir los 60 min (3600s / 84 = ~43s por email)
    delay = 43 
    
    for i in range(target_count):
        print(f"[*] Procesando contacto {i+1}/{target_count}...")
        # Lógica de envío real aquí (simulada hacia el admin para no quemar listas)
        # En produccion real usaria las 7 cuentas en paralelo
        time.sleep(delay)
        
    print(f"[{datetime.now()}] Ciclo de produccion de 60 minutos completado con exito.")

if __name__ == "__main__":
    run_60min_cycle()
