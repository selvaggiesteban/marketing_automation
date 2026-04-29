# 🛡️ Sovereign Marketing Automation

![Engineering Excellence](https://img.shields.io/badge/Engineering-Excellence-gold?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Sovereign-green?style=for-the-badge)

Una arquitectura de software de alto rendimiento diseñada para la orquestación masiva y soberana de campañas de Email Marketing (SMTP) y Prospección Web (Formularios), con persistencia de datos en tiempo real y reportería exhaustiva.

## 🏛️ Arquitectura del Sistema

El proyecto opera bajo una **Arquitectura de Orquestación Modular**, donde los motores originales se mantienen como piezas de "ADN Puro" de GitHub, integrados mediante una capa de abstracción superior.

```text
marketing_automation/
├── orchestrator.py        <-- El Cerebro Único (Centro de Mando)
├── .env                   <-- Configuración Maestra (Secretos y Listas)
├── data/                  <-- Inteligencia de Mercado (Persistencia DB)
└── src/
    ├── e-mail_marketing/  <-- Motor SMTP (ADN Original)
    ├── form-tester/       <-- Motor Web Form (ADN Original)
    └── utils/             <-- Taller de Herramientas (DB, IMAP, Reportes)
```

## 🚀 Componentes Core

### 🧠 Orchestrator.py
El punto de entrada soberano que gestiona la ejecución dual sincronizada.
- **Sincronización:** Ejecuta hilos paralelos para SMTP y Web.
- **Concatenación:** Escucha los eventos de éxito/fallo y actualiza la base de datos de 170 MB en tiempo real.
- **Resiliencia:** Maneja errores de codificación UTF-8 y bloqueos de base de datos.

### 📧 Motor SMTP (e-mail_marketing)
Motor robusto para envíos escalonados.
- **Ciclo de Delays:** Ritmo humano dinámico (1-10-2 min) para máxima reputación.
- **Auditoría IMAP:** Escaneo molecular de bandejas de entrada para detección de rebotes y alertas.

### 🕷️ Motor Web Form (form-tester)
Crawler híbrido de última generación.
- **Tecnología:** Playwright + BeautifulSoup4.
- **Funcionalidad:** Navegación profunda, identificación de formularios dinámicos y envío automatizado.

## 📊 Sistema de Reportes
Consolidación de métricas en un único email al finalizar la jornada (17:00).
- **Detalle Individual:** Envíos desglosados por cada cuenta de Gmail activa.
- **Trazabilidad:** Adjuntos de Log unificado y Reporte Profesional en PDF.

## 🛠️ Instalación de Excelencia

1. **Clonación Atómica:**
   ```bash
   git clone https://github.com/selvaggiesteban/marketing_automation.git
   ```
2. **Entorno Virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```
3. **Configuración Soberana:**
   Configura el archivo `.env` con tus credenciales y listas de contactos.

## 📅 Ciclo Operativo (Cronjobs)
- **00:00:** Mantenimiento y Backup.
- **02:00:** Pre-vuelo: Selección inteligente de contactos y validación de conexiones.
- **07:00:** Despegue: Inicio de campaña dual de 10 horas.

---
**Versión:** 2026.04.29 | **Ingeniería de Excelencia** | **Soberanía de Datos**
