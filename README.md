# 🚀 MARKETING AUTOMATION - Comando Central C3
**Autor:** [SELVAGGIESTEBAN.DEV](https://selvaggiesteban.dev)

Este repositorio es el Comando Central (C3) que orquesta y extiende la inteligencia de mis herramientas de marketing en un único entorno blindado en el VPS.

## 🔗 Repositorios Extendidos (ADN del Sistema)
Este proyecto integra de forma **literal y sin alteraciones en su lógica base** los siguientes motores:

1.  **Motor SMTP (Envío Masivo)**: [e-mail_marketing](https://github.com/selvaggiesteban/e-mail_marketing)  
    *Extensión literal del sistema de hilos, rotación y warm-up.*
2.  **Motor de Formularios (Vector Web)**: [form-tester](https://github.com/selvaggiesteban/form-tester)  
    *Integración directa para el procesamiento de dominios desde la DB.*
3.  **Analista de Auditoría**: [e-mail_marketing_reports](https://github.com/selvaggiesteban/e-mail_marketing_reports)  
    *Lógica de extracción IMAP y generación de reportes enriquecidos.*
4.  **Detector de Rebotes**: [analyze_bounces](https://github.com/selvaggiesteban/analyze_bounces)  
    *ADN de reconocimiento de patrones Mailer-Daemon en EN/ES.*
5.  **Validador de Red**: [domain_status_checker](https://github.com/selvaggiesteban/domain_status_checker)  
    *Sanitización de dominios previa al envío.*

---

## 🔍 Contraste de Integridad
Se garantiza un **Reciclaje Real**. El código contenido en la carpeta `src/` de este repositorio es una réplica funcional de los scripts originales. No se han abreviado funciones ni se han eliminado validaciones técnicas. El sistema ha sido simplemente "envuelto" para permitir:
- **Control remoto vía IMAP (Bot)**: Gestión del VPS respondiendo correos con opciones 1-5.
- **Ejecución desatendida en Crontab**: Automatización a las 07:00, 17:00 y 00:00 UTC.
- **Conectividad con contacts.db**: Consumo directo de la base de datos para envíos duales.

---

## 🛠️ Operaciones del VPS (Crontab)
Pega estas líneas en `crontab -e` tras ejecutar `./setup_vps.sh`:

```bash
# 07:00 UTC - Campaña Dual (SMTP + Forms) + Sanitización
0 7 * * 1-5 /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task campaign

# 17:00 UTC - Reporte Corporativo (Cuerpo + contacts.db adjunta)
0 17 * * 1-5 /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task report

# 00:00 UTC - Backup (Imagen Local + GDrive) + Contraste DB/CSV
0 0 * * 1-5 /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task backup

# Cada 5 min - Escucha de Comandos del Administrador (Bot IMAP)
*/5 * * * * /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task listen
```

---

## 🕹️ Menú de Comandos Remotos (Bot IMAP)
Si envías un email con el asunto de la opción al correo del VPS:
1. **REPORTE DB**: Resumen de contactos y estado de la base de datos.
2. **REPORTE CAMPAÑA**: Detalle de la última ejecución realizada.
3. **CONFIGURAR**: Cambiar Asunto/Mensaje de la próxima campaña (el sistema confirma con un OK).
4. **REMARKETING**: Iniciar hilo nuevo sobre una campaña previa (mismo remitente).
5. **FIX INTEGRIDAD**: Forzar el cruce de datos y reparación de la DB.

---
© 2026 SELVAGGIESTEBAN.DEV - Automatización de Grado Industrial.
