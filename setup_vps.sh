#!/bin/bash
# 🛠️ VPS SETUP SCRIPT - SELVAGGIESTEBAN.DEV
# Ejecutar como: chmod +x setup_vps.sh && ./setup_vps.sh

echo "------------------------------------------------"
echo "CONFIGURANDO ENTORNO MARKETING AUTOMATION"
echo "------------------------------------------------"

# 1. Actualizar sistema
sudo apt update && sudo apt install -y python3-venv rclone

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar Crontab (Borrador)
# (crontab -l ; echo "0 7 * * 1-5 /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task campaign") | crontab -
# (crontab -l ; echo "0 17 * * 1-5 /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task report") | crontab -
# (crontab -l ; echo "0 0 * * 1-5 /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task backup") | crontab -

echo "------------------------------------------------"
echo "ENTORNO LISTO. RECUERDA CONFIGURAR .env Y rclone"
echo "------------------------------------------------"
