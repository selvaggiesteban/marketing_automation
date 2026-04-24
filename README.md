# 🚀 MARKETING AUTOMATION - Manual de Operaciones
**Autor:** [SELVAGGIESTEBAN.DEV](https://selvaggiesteban.dev)
**Plataforma:** Hostinger VPS Engine

Este sistema es una suite profesional de e-mail marketing diseñada para ejecutarse de forma autónoma 24/7. Incluye motor de envío con warm-up, análisis de rebotes bilingüe, historial de campañas y remarketing dirigido.

---

## 🛠️ 1. Configuración Rápida en VPS

Si es tu primera vez en el VPS, ejecuta este comando para blindar el entorno y preparar las dependencias:

```bash
chmod +x setup_vps.sh && ./setup_vps.sh
```

---

## 📅 2. Programación de Tareas (CRON)

Para activar la automatización total (Lunes a Viernes), abre el editor de cron:
```bash
crontab -e
```
Pega estas líneas al final del archivo para programar el ciclo de hierro:

```bash
# 07:00 UTC - Inicio automático de Campaña Diaria
0 7 * * 1-5 /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task campaign

# 17:00 UTC - Generación de Reporte Corporativo y Envío a Gmail
0 17 * * 1-5 /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task report

# 00:00 UTC - Backup espejo de todo el sistema a Google Drive
0 0 * * 1-5 /root/marketing_automation/venv/bin/python /root/marketing_automation/main.py --task backup
```

---

## 🕹️ 3. Grupos de Comandos (Casos Comunes)

### 📈 Gestión de Campañas
- **Lanzar campaña actual (según .env):**
  `python main.py --task campaign`
- **Lanzar y guardar en el historial:**
  `python main.py --task campaign --name "Promo_Mayo_2026"`
- **Forzar inicio (si hay una campaña bloqueada):**
  `python main.py --task campaign --force`

### 🧠 Memoria y Re-contactación
- **Ver historial de campañas pasadas:**
  `python main.py --task history`
- **Repetir una campaña antigua (por ID):**
  `python main.py --task campaign --load 5`

### 🎯 Remarketing Dirigido (Mismo Remitente)
Envía un nuevo mensaje a quienes recibieron un asunto previo, manteniendo la conversación con el mismo usuario de Gmail original:
```bash
python main.py --task remarketing --from_subject "Hola" --new_subject "Re: Seguimiento" --new_message "mensajes/seguimiento.md"
```

### 📊 Auditoría y Resguardo
- **Generar reporte detallado ahora:**
  `python main.py --task report`
- **Ejecutar backup manual a Drive:**
  `python main.py --task backup`

---

## 🛠️ 4. Habilidades y Utilidades Extra

- **Aislamiento Total:** El sistema corre en un `venv` para evitar conflictos con actualizaciones de Hostinger.
- **Detección de Bounces:** Analiza automáticamente rebotes en Inglés y Español para limpiar tus listas.
- **Sistema Anti-Bloqueo:** No permite lanzar dos campañas en paralelo para proteger la reputación de tus cuentas de Gmail.
- **Warm-up Inteligente:** Aplica pausas de 1 a 10 minutos automáticamente entre cada envío.
- **Rotación de 7 Cuentas:** Distribuye los contactos en 7 hilos paralelos para maximizar el volumen diario.

## 📂 Ubicación de Archivos Críticos
- **Logs de Envío:** `/logs/task_campaign_*.log`
- **Base de Datos de Memoria:** `/logs/marketing_memory.db`
- **Reportes CSV:** `/logs/reporte_corporativo_*.csv`

---
© 2026 SELVAGGIESTEBAN.DEV - Sistemas de Alta Disponibilidad.
