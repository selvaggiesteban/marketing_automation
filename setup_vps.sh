#!/bin/bash
# 🛠️ VPS SETUP C3 ENGINE - SELVAGGIESTEBAN.DEV
echo "------------------------------------------------"
echo "INSTALANDO SISTEMA CENTRAL DE COMANDO C3"
echo "------------------------------------------------"

# 1. Dependencias de Sistema (Rsync para backup local, Sqlite para DB)
sudo apt update && sudo apt install -y python3-venv rclone rsync sqlite3

# 2. Preparar directorios blindados
mkdir -p data logs reports venv

# 3. Entorno Virtual y Dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Parchear base de datos si existe
python scripts/db_patcher.py

echo "------------------------------------------------"
echo "SISTEMA LISTO Y EN ARMONÍA."
echo "------------------------------------------------"
