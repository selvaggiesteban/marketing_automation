# Gateway para VPS Hostinger - Versión Sincronizada
# Configuración extraída de DATOS.MD

$vps_ip = "72.60.59.25"
$vps_user = "root"
$vps_pass = "g(5WWkmj8&9#JsMQ"
$project_path = "/root/email-marketing"

function Show-Menu {
    Write-Host "`n--- VPS GATEWAY (Hostinger) ---" -ForegroundColor Cyan
    Write-Host "1. Probar conexión SSH"
    Write-Host "2. Preparar Entorno Seguro (Venv + Deps)"
    Write-Host "3. Desplegar Proyecto (Código + Campañas)"
    Write-Host "4. Iniciar Campaña en VPS (Screen)"
    Write-Host "5. Ver Progreso en Vivo (Attach)"
    Write-Host "6. Listar sesiones activas"
    Write-Host "Q. Salir"
}

do {
    Show-Menu
    $choice = Read-Host "Seleccione una opción"

    switch ($choice) {
        "1" {
            Write-Host "Probando conexión a $vps_ip..."
            ssh ${vps_user}@${vps_ip} "echo 'Conexión exitosa'"
        }
        "2" {
            Write-Host "Configurando entorno virtual y dependencias..."
            ssh ${vps_user}@${vps_ip} "apt update && apt install -y python3-pip python3.12-venv screen && mkdir -p $project_path && cd $project_path && python3 -m venv venv && ./venv/bin/pip install python-dotenv fpdf"
        }
        "3" {
            Write-Host "Transfiriendo archivos del proyecto..."
            # Crear carpeta si no existe
            ssh ${vps_user}@${vps_ip} "mkdir -p $project_path"
            # Transferir script, .env y carpeta de campañas
            scp e-mail_marketing.py .env ${vps_user}@${vps_ip}:$project_path/
            scp -r campaigns ${vps_user}@${vps_ip}:$project_path/
            Write-Host "Despliegue completado."
        }
        "4" {
            Write-Host "Iniciando campaña en sesión 'mailing'..."
            ssh ${vps_user}@${vps_ip} "cd $project_path && screen -dmS mailing ./venv/bin/python3 e-mail_marketing.py"
            Write-Host "Campaña lanzada en segundo plano."
        }
        "5" {
            Write-Host "Entrando a la sesión de monitoreo... (Presione Ctrl+A luego D para salir)"
            ssh -t ${vps_user}@${vps_ip} "screen -r mailing"
        }
        "6" {
            ssh ${vps_user}@${vps_ip} "screen -ls"
        }
    }
} while ($choice -ne "Q")
