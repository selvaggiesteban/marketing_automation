<div align="center">

```
    ███████╗ ██████╗ ██████╗ ███╗   ███╗    ████████╗███████╗███████╗████████╗███████╗██████╗
    ██╔════╝██╔═══██╗██╔══██╗████╗ ████║    ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
    █████╗  ██║   ██║██████╔╝██╔████╔██║       ██║   █████╗  ███████╗   ██║   █████╗  ██████╔╝
    ██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║       ██║   ██╔══╝  ╚════██║   ██║   ██╔══╝  ██╔══██╗
    ██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║       ██║   ███████╗███████║   ██║   ███████╗██║  ██║
    ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝       ╚═╝   ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
```

**🤖 Automated Contact Form Testing with Pipeline Architecture**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Playwright](https://img.shields.io/badge/Playwright-✓-45ba4b.svg)](https://playwright.dev)
[![Async](https://img.shields.io/badge/Async-✓-ff69b4.svg)](https://docs.python.org/3/library/asyncio.html)
[![Pipeline](https://img.shields.io/badge/Pipeline-1Crawler+1Sender-orange.svg)](#architecture)

**Crawl → Queue → Send → Report**

[🚀 Quick Start](#quick-start) • [📖 Documentation](#documentation) • [⚙️ Configuration](#configuration) • [🏗️ Architecture](#architecture)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Pipeline Mode](#pipeline-mode)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [File Formats](#file-formats)
- [Reason Codes](#reason-codes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🎯 Overview

**Form Tester** is a production-grade CLI tool designed for automated testing of contact forms across multiple websites. It uses a **Pipeline Architecture** with **1 Crawler** and **1 Sender** working independently through an async queue, with a **3-minute rate limit** between sends.

### Pipeline Philosophy

Unlike traditional sequential processing, Form Tester separates the crawling phase from the sending phase:

| Phase | Worker | Behavior | Independence |
|-------|--------|----------|--------------|
| **Crawl** | 1 Worker | Sequential domain processing | Doesn't wait for sends |
| **Queue** | Async Buffer | Unbounded storage | Decouples phases |
| **Send** | 1 Worker | 3-minute rate limited | Doesn't block crawling |

This means while the sender is waiting 3 minutes between sends, the crawler continues processing the next domains.

---

## ✨ Key Features

### 🔎 Discovery & Detection
- **Hybrid Crawling**: Fast static analysis (`httpx` + `BeautifulSoup`) with JavaScript-enabled fallback (`Playwright`)
- **Smart URL Discovery**: Prioritizes `/contacto`, `/contact` paths and follows internal links
- **Multi-language Support**: Recognizes form fields in English, Spanish, French, Italian, and Portuguese
- **Email Extraction**: Scans for `mailto:` links and plaintext patterns for SMTP fallback

### 🤖 Intelligent Interaction
- **Popup Dismissal**: Automatically closes cookie banners, GDPR modals, and newsletter overlays
- **Mandatory Checkboxes**: Checks Terms & Conditions and Privacy Policy boxes
- **AJAX Aware**: Waits for responses from Contact Form 7, Elementor, and other plugins
- **Field Mapping**: Auto-detects name, email, phone, company, and message fields

### 🛡️ Protection & Fallback
- **CAPTCHA Detection**: Detects reCAPTCHA (v2/v3), hCAPTCHA, and generic security codes
- **Honeypot Detection**: Identifies hidden fields and CSS-obfuscated spam traps
- **SMTP Fallback**: Automatically sends email if form is protected or fails
- **Bounce Tracking**: Maintains `suppression_list.csv` to prevent retrying bad emails

### 📊 Evidence & Reporting
- **Console Logging**: Full execution logs saved to `evidence/{domain}_{timestamp}.log`
- **Progress Tracking**: Real-time statistics showing domains processed, URLs analyzed, emails extracted
- **Structured Results**: CSV output with machine-readable reason codes

---

## 🏗️ Architecture

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PIPELINE ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────────────┐     │
│   │   domains   │─────▶│   Crawler   │─────▶│   PipelineQueue     │     │
│   │    .csv     │      │   (1×)      │      │   (async.Queue)     │     │
│   └─────────────┘      └─────────────┘      └──────────┬──────────┘     │
│                                                        │                 │
│   Sequential crawling:                                 │                 │
│   • Domain 1 crawled                                   │                 │
│   • Domain 2 crawled ──────────────────────────────────┤                 │
│   • Domain 3 crawled ──────────────────────────────────┤                 │
│   • ... etc                                            ▼                 │
│                                               ┌─────────────────────┐    │
│                                               │   Sender (1×)       │    │
│                                               │   Rate Limited      │    │
│                                               └──────────┬──────────┘    │
│                                                          │              │
│   Sends with 3-min delay:                                │              │
│   • Domain 1 sent ◄──────┐                               │              │
│   • Wait 3 minutes       │                               │              │
│   • Domain 2 sent ◄────────┘                               │              │
│   • Wait 3 minutes                                         │              │
│   • Domain 3 sent ◄──────────────────────────────────────┘              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why Pipeline?

**Traditional Sequential Mode:**
```
Domain 1 → Crawl → Wait 3min → Send → Domain 2 → Crawl → Wait 3min → Send...
Total time: N × (crawl_time + 3min)
```

**Pipeline Mode:**
```
Crawler:  Domain 1 → Domain 2 → Domain 3 → Domain 4... (continuous)
Sender:   Domain 1 → [3min] → Domain 2 → [3min] → Domain 3...
Total time: crawl_all + (N × 3min) - overlap
```

The crawler never waits for the sender. While sender waits 3 minutes, crawler processes the next domain.

---

## 🚀 Quick Start

### 1. Install

```bash
# Clone the repository
git clone https://github.com/selvaggiesteban/form-tester.git
cd form-tester

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: .\venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### 2. Configure

```bash
# Copy environment template
cp .env.example .env

# Edit with your SMTP credentials
nano .env  # or notepad .env on Windows
```

**Required environment variables:**
```bash
FORM_TESTER_SMTP_USER=your-email@gmail.com
FORM_TESTER_SMTP_PASSWORD=your-app-password
FORM_TESTER_FROM_EMAIL=your-email@gmail.com
```

### 3. Initialize

```bash
# Create sample files
python main.py init

# This creates:
# - domains.csv        # List of domains to test
# - evidence/          # Log files directory
# - smtp_accounts.csv  # Optional: multiple SMTP accounts
# - messages.csv       # Optional: message templates
# - contacts.csv       # Optional: contact data rotation
```

### 4. Run

```bash
# Test single domain
python main.py process --domain example.com

# Process all domains from domains.csv
python main.py process

# Schedule for later
python main.py process --schedule "2025-12-31 23:59"
```

---

## 📦 Installation

### Prerequisites
- **Python 3.8+**
- **pip** & **Git**

### Platform Setup

#### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

#### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

---

## 💻 Usage

### Commands

| Command | Description |
|---------|-------------|
| `python main.py init` | Creates sample files and directories |
| `python main.py process` | Process all domains in pipeline mode |
| `python main.py process --domain example.com` | Test single domain |
| `python main.py process --schedule "2025-12-31 23:59"` | Schedule execution |
| `python main.py suppress user@domain.com` | Add email to suppression list |

### Pipeline Execution

The tool always runs in **pipeline mode**:

1. **Crawler** processes domains sequentially (one at a time)
2. **Queue** stores crawled results (forms + emails)
3. **Sender** processes queue with 3-minute delay between sends

**Example output:**
```
======================================================================
🚀 Modo: Pipeline (1 Crawler + 1 Sender)
   Dominios: 10
   Delay entre envíos: 3 minutos
======================================================================

🕷️  Crawler iniciado - 10 dominios
======================================================================
🌐 Crawleando: example1.com
  ✅ Encolado para envío: example1.com
🌐 Crawleando: example2.com
  ✅ Encolado para envío: example2.com
...

📤 Sender iniciado - esperando items...
   Rate limit: 3 minutos entre envíos
======================================================================
  🚀 Iniciando envío para: example1.com
  ✅ Formulario enviado
  ⏱️  Esperando 3.0 min para rate limit...
  🚀 Iniciando envío para: example2.com
  ✅ Email enviado a contact@example2.com
...
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FORM_TESTER_SMTP_USER` | Yes | SMTP username (Gmail) |
| `FORM_TESTER_SMTP_PASSWORD` | Yes | App-specific password |
| `FORM_TESTER_FROM_EMAIL` | No | Override "From" address |
| `FORM_TESTER_PROXY_URL` | No | SOCKS5/HTTP Proxy |
| `LOG_LEVEL` | No | Set to `DEBUG` for verbose logs |

### Code Configuration (main.py)

```python
# Crawler Settings
MAX_PAGES_PER_DOMAIN = 10       # Max pages to crawl per domain
RATE_LIMIT_DELAY = 1.0          # Seconds between HTTP requests
REQUEST_TIMEOUT = 30            # HTTP timeout in seconds

# Send Settings (hardcoded)
SEND_DELAY_MINUTES = 3          # 3-minute delay between sends

# Test Data
TEST_DATA = {
    "name": "Your Name",
    "email": "your@email.com",
    "phone": "+1-555-123-4567",  # Use hyphens for validation
    "message": "Your test message..."
}
```

---

## 📁 File Formats

### domains.csv

```csv
example.com,contact@example.com
testsite.org
another.com,sales@another.com
```

- One domain per line
- Optional email for pre-filled target

### results.csv

```csv
timestamp,domain,action,status,reason_code,reason_description,details,evidence_path
2025-03-12 14:30:00,example.com,FORM_SUBMIT,SUCCESS,FORM_SUBMITTED_SUCCESS,Form submitted successfully,Form at https://example.com/contact,evidence/example.com_20250312_143000.log
```

### extracted_emails.csv

Generated at end of run:
```csv
domain,email,extraction_date
example.com,contact@example.com,2025-03-12
```

---

## 🏷️ Reason Codes

| Code | Status | Description |
|------|--------|-------------|
| `FORM_SUBMITTED_SUCCESS` | ✅ Success | Form submitted via Playwright |
| `EMAIL_SENT` | ✅ Success | Email sent via SMTP fallback |
| `HAS_RECAPTCHA` | ⚠️ Fallback | reCAPTCHA detected, SMTP fallback used |
| `HAS_H_CAPTCHA` | ⚠️ Fallback | hCAPTCHA detected, SMTP fallback used |
| `HONEYPOT_DETECTED` | ⚠️ Fallback | Honeypot detected, SMTP fallback used |
| `FORM_VALIDATION_FAILED` | ❌ Failed | Form validation error |
| `NO_FORM_FOUND` | ⚠️ Fallback | No form found, tried SMTP |
| `NO_EMAIL_FOUND` | ❌ Failed | No contact method found |
| `HARD_BOUNCE` | ❌ Failed | Email bounced, added to suppression list |
| `SUPPRESSED` | ⏭️ Skipped | Email in suppression list |
| `BLACKLISTED` | ⏭️ Skipped | Domain in blacklist |

---

## 🐛 Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: src.pipeline_queue`, ensure:
```bash
# You're in the project root
cd /path/to/form-tester

# Virtual environment is activated
source venv/bin/activate
```

### Form Validation Failed

Check `evidence/{domain}_{timestamp}.log` for detailed error messages.

### Rate Limiting Not Working

The 3-minute delay is between sends, not between crawls. The crawler continues while sender waits.

### SMTP Authentication Failed

- Use App Password (not regular password) for Gmail
- Enable 2FA on Gmail account
- Generate App Password at: Google Account → Security → 2FA → App passwords

---

## 📊 Project Structure

```
form-tester/
├── main.py                    # Main CLI entry point
├── src/                       # Pipeline modules
│   ├── __init__.py
│   ├── pipeline_queue.py     # Async queue between crawler/sender
│   ├── rate_limiter.py         # 3-minute rate limiter
│   ├── crawler_worker.py       # Single crawler worker
│   ├── sender_worker.py        # Single sender worker
│   └── pipeline_runner.py      # Orchestrates pipeline
├── tests/                     # Test files
│   ├── test_pipeline_queue.py
│   └── test_rate_limiter.py
├── domains.csv                # Input: domains to test
├── results.csv                # Output: submission results
├── suppression_list.csv       # Bounced emails
├── extracted_emails.csv       # Found emails
├── evidence/                  # Log files
│   └── {domain}_{timestamp}.log
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── README.md                  # This file
```

---

## 🏗️ Pipeline Architecture Details

### Components

1. **PipelineQueue** (`src/pipeline_queue.py`)
   - Unbounded `asyncio.Queue` between phases
   - Tracks completed items for graceful shutdown

2. **RateLimiter** (`src/rate_limiter.py`)
   - Enforces 3-minute delay between sends
   - Async-safe with locking

3. **CrawlerWorker** (`src/crawler_worker.py`)
   - Sequential domain processing
   - Enqueues results immediately after crawling

4. **SenderWorker** (`src/sender_worker.py`)
   - Waits on queue (blocking)
   - Applies rate limit before each send
   - Handles CAPTCHA/honeypot fallbacks

5. **PipelineRunner** (`src/pipeline_runner.py`)
   - Coordinates both workers with `asyncio.gather()`
   - Manages shared resources

### Concurrency Model

```python
# Simplified view
crawler_task = asyncio.create_task(crawler.run(tasks))
sender_task = asyncio.create_task(sender.run())

await asyncio.gather(crawler_task, sender_task)
```

Both tasks run concurrently, communicating only through the queue.

---

## 📝 License

MIT License - Copyright (c) 2025 Esteban Selvaggi.

See [LICENSE](LICENSE) for full text.

---

<div align="center">

**Made with ❤️ by Esteban Selvaggi**

[Website](https://selvaggiesteban.dev) • [GitHub](https://github.com/selvaggiesteban) • [LinkedIn](https://linkedin.com/in/esteban-selvaggi)

</div>
