# 🚀 E-mail Marketing Automation Engine

**The ultimate high-performance engine for precision email marketing.** This suite is engineered to bypass common deliverability hurdles using multi-account orchestration, human-mimicking behavior, and automated bounce management.

---

## 📌 Strategic Overview
This automation suite allows businesses to scale their outreach by distributing campaigns across multiple SMTP accounts in parallel. It handles the complexities of SMTP rate limits, sender reputation, and real-time bounce tracking automatically, ensuring your message actually reaches the inbox.

## ⚡ Key Technical Features
*   **Orchestrated Multi-Account Delivery**: Intelligent distribution of contacts across multiple SMTP providers to maximize throughput without triggering flags.
*   **Anti-Spam reputation Shield**: Implements dynamic delay cycles (1 to 10-minute intervals) to mimic human behavior and preserve sender reputation.
*   **🔍 AI-Powered Bounce Intelligence**: Integrated IMAP engine that scans all sender inboxes for `MAILER-DAEMON` notifications.
    *   **Bilingual Detection**: Support for English & Spanish failure patterns (e.g., "Address not found" / "Dirección no encontrada").
*   **Seamless VPS Gateway**: Built-in PowerShell automation for one-click deployment to Hostinger VPS environments.
*   **Professional Audit Reports**: Automatic generation of human-readable PDF reports and detailed execution logs for every campaign.

## 🏗 System Architecture
*   **Backend**: Python 3.12 with `threading` for concurrent scanning.
*   **Security**: Strict environment isolation via `python-dotenv` and protected campaign data via `.gitignore`.
*   **Persistence**: `screen`-ready for 24/7 execution in cloud environments.

## 🚦 Quick Start Guide

### 1. Prerequisites
- Python 3.12+
- Gmail accounts with **App Passwords** enabled.
- IMAP access enabled in your email settings.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/selvaggiesteban/e-mail_marketing.git
cd e-mail_marketing

# Install dependencies
pip install python-dotenv fpdf
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
CAMPAIGN_ID=CMP-2026
SUBJECT=Business Proposition
CONTACT_LIST=campaigns/e-mail/date/emails.txt
MESSAGE=campaigns/e-mail/date/message.md
SMTP_ACCOUNTS=email1@gmail.com|pass,email2@gmail.com|pass
```

### 4. Deployment (Local or VPS)
- **Local**: `python e-mail_marketing.py`
- **VPS**: Use the `vps_gateway.ps1` or run via `screen` for persistent delivery.

## 📊 Directory Structure
```text
.
├── e-mail_marketing.py   # Main engine
├── vps_gateway.ps1       # VPS Automation tool
├── .env                  # Secret configuration
└── campaigns/            # Encapsulated campaign data
    ├── contacts/         # Database and HTML contact lists
    └── e-mail/           # Segmented daily campaigns & logs
```

---
**Developed with precision by Esteban Selvaggi**  
🌐 [selvaggiesteban.dev](https://selvaggiesteban.dev/) | 📧 [hola@selvaggiesteban.dev](mailto:hola@selvaggiesteban.dev)
