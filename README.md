# 🚀 MARKETING AUTOMATION - VPS ENGINE
**Autor:** [SELVAGGIESTEBAN.DEV](https://selvaggiesteban.dev)
**Versión:** 1.0.0 (24-04-2026)

Sistema profesional de automatización de marketing diseñado para despliegue en VPS (Ubuntu/Debian). Este repositorio integra el motor de envíos masivos, el generador de reportes corporativos y el sistema de backups redundantes en Google Drive.

## 📦 Componentes del Sistema

1. **Engine (07:00 UTC)**: Motor de envío masivo vía SMTP con rotación de cuentas de Gmail.
2. **Reporter (17:00 UTC)**: Analizador IMAP de "Enviados" y "Bounces" para auditoría total.
3. **Guard (00:00 UTC)**: Sincronización espejo con Google Drive mediante Rclone.

## 🛠️ Instalación en VPS (Fast Setup)

Para configurar el entorno virtual y las dependencias en tu VPS Hostinger:

```bash
chmod +x setup_vps.sh
./setup_vps.sh
```

## ⚙️ Configuración (.env)
El sistema requiere un archivo `.env` en la raíz con:
- `SMTP_ACCOUNTS`: Cuentas de envío (formato email|pass).
- `RECIPIENT_REPORT`: Email donde se recibe el reporte corporativo.
- `RCLONE_REMOTE`: Nombre del remoto configurado en Rclone.

## 📊 Ciclo de Vida Diario (CRON)
| Hora (UTC) | Tarea | Descripción |
| :--- | :--- | :--- |
| 07:00 | `campaign_manager.py` | Envío de campaña diaria. |
| 17:00 | `report_generator.py` | Generación y envío de reporte CSV. |
| 00:00 | `backup_manager.py` | Backup espejo a Google Drive. |

---
© 2026 SELVAGGIESTEBAN.DEV - Todos los derechos reservados.
