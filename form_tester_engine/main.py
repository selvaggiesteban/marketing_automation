#!/usr/bin/env python3
"""
Form Tester - Automated Contact Form Testing Tool
Author: Esteban Selvaggi
Website: https://selvaggiesteban.dev
Repository: https://github.com/selvaggiesteban/form-tester.git

A command-line tool that crawls websites, identifies contact forms,
submits test data, and falls back to SMTP email delivery when forms
are unavailable or protected by anti-spam measures.
"""

# =============================================================================
# CONFIGURATION SECTION - Modify these settings as needed
# =============================================================================

# SMTP Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = ""  # Set via environment variable: FORM_TESTER_SMTP_USER
SMTP_PASSWORD = ""  # Set via environment variable: FORM_TESTER_SMTP_PASSWORD
SMTP_FROM_EMAIL = ""  # Set via environment variable: FORM_TESTER_FROM_EMAIL

# Test Data - Configure with your own information
TEST_DATA = {
    "name": "Esteban Selvaggi",
    "email": "selvaggiesteban9@gmail.com",
    "subject": "Hola",
    "message": "Hola envié un mensaje desde el formulario web y no recibí respuesta. Quiero saber si recibieron mi mensaje.",
    "phone": "+54-9-11-5332-3937",  # Use hyphens, not spaces, for pattern validation
    "company": "Esteban Selvaggi",
}

# Crawler Settings
MAX_PAGES_PER_DOMAIN = 10
REQUEST_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
RATE_LIMIT_DELAY = 1.0  # Seconds between requests to same domain
MAX_RETRIES = 3

# Form Detection
FORM_FIELD_MAPPINGS = {
    "name": [
        "name", "nombre", "fullname", "full_name", "your_name", "contact_name",
        "first_name", "last_name", "firstname", "lastname", "apellido", "nombres",
        "from_name", "user_name", "customer_name", "client_name", "visitor_name",
        "nom", "prenom", "nome", "cognome"
    ],
    "email": [
        "email", "correo", "e-mail", "mail", "email_address", "your_email",
        "from_email", "contact_email", "user_email", "customer_email", "client_email",
        "visitor_email", "reply_to", "replyto", "correo_electronico", "email_destinatario",
        "adresse_email", "courriel", "indirizzo_email"
    ],
    "subject": [
        "subject", "asunto", "topic", "title", "tema", "motivo", "razon",
        "subject_line", "mail_subject", "message_subject", "consulta_subject",
        "about", "regarding", "re", "asunto_del_mensaje", "titulo",
        "sujet", "objet", "oggetto", "assunto"
    ],
    "message": [
        "message", "mensaje", "comments", "comment", "body", "content", "your_message",
        "msg", "text", "description", "details", "consulta", "consultation",
        "query", "inquiry", "question", "note", "notes", "additional_info",
        "more_info", "informacion_adicional", "mensaje_adicional", "comentarios",
        "textarea", "your_message_text", "message_body", "mail_body",
        "votre_message", "votre_commentaire", "il_tuo_messaggio"
    ],
    "phone": [
        "phone", "telefono", "tel", "telephone", "mobile", "cell", "cellphone",
        "phone_number", "telefono_fijo", "celular", "movil", "numero_telefono",
        "contact_number", "phone_no", "tel_no", "mobile_number", "telefono_contacto",
        "telephone_portable", "numero_de_telephone", "telefono_cellulare"
    ],
    "company": [
        "company", "empresa", "organization", "business", "firma", "organizacion",
        "company_name", "business_name", "organization_name", "nombre_empresa",
        "work_place", "workplace", "employer", "entidad", "razon_social",
        "societe", "entreprise", "societa", "azienda", "empresa_nome"
    ],
}

# Output Files
DOMAINS_FILE = "domains.csv"
RESULTS_FILE = "results.csv"
SUPPRESSION_FILE = "suppression_list.csv"
EVIDENCE_DIR = "evidence"

# Domain Blacklist - Skip these domains
BLACKLISTED_DOMAINS = [
    "ejemplo.com", "webador.es", "doctoralia.com", "example.com", "mail.com", "sentry.wixpress.com", "gurusoluciones.com", "envato.com", "email.com", "some.com", "sentry-next.wixpress.com", "sentry.io", "company.com", "facebook.com", "instagram.com", "linkedin.com", "tiktok.com", "youtube.com", "whatsapp.com", "wa.me", "fb.me", "fb.com", "argentina.gob.ar", "buenosaires.gob.ar", "booking.com", "bluepillow.com", "gurugo.com.ar", "mercadolibre.com", "registroautomotor.info", "sanisidro.gob.ar", "tigre.gov.ar", "w.app", "zonaprop.com.ar", "calendly.com", "canva.com", "business.google.com",
]

# Blacklisted file extensions - Skip URLs ending with these
BLACKLISTED_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".rar", ".tar", ".gz", ".7z",
    ".mp3", ".mp4", ".avi", ".mov", ".wmv",
    ".js", ".css", ".json", ".xml",
]

# Reason Codes for logging
REASON_CODES = {
    "FORM_SUBMITTED_SUCCESS": "Formulario enviado exitosamente",
    "HAS_RECAPTCHA": "reCAPTCHA detectado, envío omitido",
    "HAS_HCAPTCHA": "hCAPTCHA detectado, envío omitido",
    "NO_FORM_FOUND": "No se encontró formulario de contacto",
    "EMAIL_SENT": "Email enviado vía SMTP como fallback",
    "HARD_BOUNCE": "Bounce permanente detectado, agregado a suppression list",
    "FORM_FILL_ERROR": "Error al completar campos del formulario",
    "HONEYPOT_DETECTED": "Honeypot detectado, envío omitido",
    "NETWORK_ERROR": "Error de red al acceder al sitio",
    "TIMEOUT_ERROR": "Timeout en la solicitud",
    "SMTP_ERROR": "Error al enviar email vía SMTP",
    "UNKNOWN_ERROR": "Error desconocido",
    "SUPPRESSED": "Email en lista de supresión",
    "FORM_VALIDATION_FAILED": "Validación del formulario fallida",
}

# =============================================================================
# IMPORTS
# =============================================================================

import asyncio
import csv
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import click
import httpx
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Override config with environment variables
SMTP_USER = os.getenv("FORM_TESTER_SMTP_USER", SMTP_USER)
SMTP_PASSWORD = os.getenv("FORM_TESTER_SMTP_PASSWORD", SMTP_PASSWORD)
SMTP_FROM_EMAIL = os.getenv("FORM_TESTER_FROM_EMAIL", SMTP_FROM_EMAIL)

# Proxy Configuration (optional)
PROXY_URL = os.getenv("FORM_TESTER_PROXY_URL", "")
HTTP_PROXY = os.getenv("FORM_TESTER_HTTP_PROXY", "")
HTTPS_PROXY = os.getenv("FORM_TESTER_HTTPS_PROXY", "")


# =============================================================================
# LOGGING SETUP - Captures console output to evidence folder
# =============================================================================

class EvidenceLogger:
    """Logger that writes to both console and a log file in evidence folder."""

    def __init__(self, browser=None):
        self.browser = browser
        self.log_file = None
        self.log_path = None

    def set_log_file(self, domain: str):
        """Set up log file for a specific domain."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_domain = domain.replace(".", "_").replace("/", "_")
        self.log_path = Path(EVIDENCE_DIR) / f"{safe_domain}_{timestamp}.log"
        Path(EVIDENCE_DIR).mkdir(exist_ok=True)
        self.log_file = open(self.log_path, "w", encoding="utf-8")

    def close(self):
        """Close the log file."""
        if self.log_file:
            self.log_file.close()
            self.log_file = None

    def log(self, message: str):
        """Write message to console and log file."""
        # Write to console
        click.echo(message)
        # Write to file with timestamp
        if self.log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_file.write(f"[{timestamp}] {message}\n")
            self.log_file.flush()

    def get_log_path(self) -> Optional[str]:
        """Return the current log file path."""
        return str(self.log_path) if self.log_path else None


# Global logger instance
evidence_logger = EvidenceLogger()


def log(message: str):
    """Helper function to log to both console and file."""
    evidence_logger.log(message)


# =============================================================================
# STATISTICS TRACKER - Para mostrar progreso en tiempo real
# =============================================================================

class Statistics:
    """Tracks real-time statistics for the crawling and submission process."""

    def __init__(self, browser=None):
        self.browser = browser
        self.domains_total = 0
        self.domains_processed = 0
        self.urls_analyzed = 0
        self.urls_valid = 0
        self.urls_invalid = 0
        self.emails_found = 0
        self.emails_extracted = set()  # Para evitar duplicados
        self.messages_sent = 0
        self.messages_failed = 0
        self.forms_submitted = 0
        self.forms_failed = 0
        self.start_time = None
        self.emails_by_domain = {}  # Para almacenar emails por dominio

    def start(self):
        """Mark the start time."""
        self.start_time = datetime.now()

    def set_total_domains(self, total: int):
        """Set total number of domains to process."""
        self.domains_total = total

    def increment_domain(self):
        """Increment processed domains counter."""
        self.domains_processed += 1

    def add_urls_analyzed(self, count: int, valid: bool = True):
        """Add analyzed URLs."""
        self.urls_analyzed += count
        if valid:
            self.urls_valid += count
        else:
            self.urls_invalid += count

    def add_emails_found(self, emails: Set[str], domain: str = ""):
        """Add found emails."""
        new_emails = emails - self.emails_extracted
        self.emails_found += len(new_emails)
        self.emails_extracted.update(new_emails)
        if domain:
            if domain not in self.emails_by_domain:
                self.emails_by_domain[domain] = set()
            self.emails_by_domain[domain].update(emails)

    def increment_message_sent(self, success: bool = True):
        """Increment message sent counter."""
        if success:
            self.messages_sent += 1
        else:
            self.messages_failed += 1

    def increment_form_submitted(self, success: bool = True):
        """Increment form submission counter."""
        if success:
            self.forms_submitted += 1
        else:
            self.forms_failed += 1

    def get_progress(self) -> str:
        """Get formatted progress string."""
        elapsed = ""
        if self.start_time:
            delta = datetime.now() - self.start_time
            elapsed = f"Tiempo: {delta.seconds//60}m {delta.seconds%60}s | "

        domain_pct = (self.domains_processed / self.domains_total * 100) if self.domains_total > 0 else 0

        return (
            f"\n{'='*70}\n"
            f"📊 PROGRESO ({elapsed}Dominio {self.domains_processed}/{self.domains_total} - {domain_pct:.1f}%)\n"
            f"{'='*70}\n"
            f"  URLs analizadas: {self.urls_analyzed} | Válidas: {self.urls_valid} | Inválidas: {self.urls_invalid}\n"
            f"  Emails extraídos: {self.emails_found} (únicos: {len(self.emails_extracted)})\n"
            f"  Mensajes enviados: {self.messages_sent} | Fallidos: {self.messages_failed}\n"
            f"  Formularios enviados: {self.forms_submitted} | Fallidos: {self.forms_failed}\n"
            f"{'='*70}"
        )

    def save_emails_to_file(self, filename: str = "extracted_emails.csv"):
        """Save all extracted emails to a CSV file."""
        path = Path(filename)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["domain", "email", "extraction_date"])
            for domain, emails in self.emails_by_domain.items():
                for email in emails:
                    writer.writerow([domain, email, datetime.now().isoformat()])
        return str(path)


# Global statistics instance
stats = Statistics()


# =============================================================================
# LIBRARY SYSTEM - Cuentas SMTP, Mensajes y Contactos
# =============================================================================

class MessageLibrary:
    """Manages SMTP accounts, message templates, and contact data."""

    def __init__(self, browser=None):
        self.browser = browser
        self.smtp_accounts = []
        self.current_account_index = 0
        self.message_templates = []
        self.current_template_index = 0
        self.contact_data_list = []
        self.current_contact_index = 0

        # Load data from library files
        self._load_smtp_accounts()
        self._load_message_templates()
        self._load_contact_data()

    def _load_smtp_accounts(self):
        """Load SMTP accounts from smtp_accounts.csv."""
        path = Path("smtp_accounts.csv")
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.smtp_accounts.append({
                        "host": row.get("host", "smtp.gmail.com"),
                        "port": int(row.get("port", 587)),
                        "user": row.get("user", ""),
                        "password": row.get("password", ""),
                        "from_email": row.get("from_email", row.get("user", "")),
                    })
        # Si no hay cuentas en archivo, usar la configuración por defecto
        if not self.smtp_accounts and SMTP_USER:
            self.smtp_accounts.append({
                "host": SMTP_HOST,
                "port": SMTP_PORT,
                "user": SMTP_USER,
                "password": SMTP_PASSWORD,
                "from_email": SMTP_FROM_EMAIL or SMTP_USER,
            })

    def _load_message_templates(self):
        """Load message templates from messages.csv."""
        path = Path("messages.csv")
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.message_templates.append({
                        "name": row.get("name", "default"),
                        "subject": row.get("subject", TEST_DATA["subject"]),
                        "body": row.get("body", TEST_DATA["message"]),
                    })
        # Si no hay templates, usar el default
        if not self.message_templates:
            self.message_templates.append({
                "name": "default",
                "subject": TEST_DATA["subject"],
                "body": TEST_DATA["message"],
            })

    def _load_contact_data(self):
        """Load contact data from contacts.csv."""
        path = Path("contacts.csv")
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.contact_data_list.append({
                        "name": row.get("name", TEST_DATA["name"]),
                        "email": row.get("email", TEST_DATA["email"]),
                        "phone": row.get("phone", TEST_DATA["phone"]),
                        "company": row.get("company", TEST_DATA["company"]),
                        "subject": row.get("subject", TEST_DATA["subject"]),
                        "message": row.get("message", TEST_DATA["message"]),
                    })
        # Si no hay contactos, usar el default
        if not self.contact_data_list:
            self.contact_data_list.append(TEST_DATA.copy())

    def get_next_smtp_account(self) -> Dict:
        """Get next SMTP account (rotation)."""
        if not self.smtp_accounts:
            return {
                "host": SMTP_HOST,
                "port": SMTP_PORT,
                "user": SMTP_USER,
                "password": SMTP_PASSWORD,
                "from_email": SMTP_FROM_EMAIL or SMTP_USER,
            }
        account = self.smtp_accounts[self.current_account_index]
        self.current_account_index = (self.current_account_index + 1) % len(self.smtp_accounts)
        return account

    def get_next_message_template(self) -> Dict:
        """Get next message template (rotation)."""
        if not self.message_templates:
            return {
                "subject": TEST_DATA["subject"],
                "body": TEST_DATA["message"],
            }
        template = self.message_templates[self.current_template_index]
        self.current_template_index = (self.current_template_index + 1) % len(self.message_templates)
        return template

    def get_next_contact_data(self) -> Dict:
        """Get next contact data (rotation)."""
        if not self.contact_data_list:
            return TEST_DATA.copy()
        data = self.contact_data_list[self.current_contact_index]
        self.current_contact_index = (self.current_contact_index + 1) % len(self.contact_data_list)
        return data

    def get_stats(self) -> str:
        """Get library statistics."""
        return (
            f"📚 Biblioteca cargada:\n"
            f"   - Cuentas SMTP: {len(self.smtp_accounts)}\n"
            f"   - Templates de mensajes: {len(self.message_templates)}\n"
            f"   - Datos de contacto: {len(self.contact_data_list)}"
        )


# Global library instance
message_lib = MessageLibrary()


# =============================================================================
# DATA CLASSES
# =============================================================================

class DomainTask:
    """Represents a task for processing a domain."""

    def __init__(self, domain: str, target_email: str = ""):
        self.domain = domain
        self.target_email = target_email
        self.visited_urls: Set[str] = set()
        self.forms_found: List[Dict] = []
        self.emails_found: Set[str] = set()
        self.results: List[Dict] = []


class FormData:
    """Represents a detected contact form."""

    def __init__(self, url: str, html: str, fields: Dict, submit_button: Optional[str] = None):
        self.url = url
        self.html = html
        self.fields = fields
        self.submit_button = submit_button
        self.has_captcha = False
        self.has_honeypot = False
        self.captcha_type: Optional[str] = None


# =============================================================================
# CSV HANDLING
# =============================================================================

def is_domain_blacklisted(domain: str) -> bool:
    """Check if a domain is in the blacklist.

    Checks against:
    - Blacklisted domain names (exact or partial match)
    - Blacklisted file extensions
    """
    domain_lower = domain.lower()

    # Check against blacklisted domains
    for blacklisted in BLACKLISTED_DOMAINS:
        if blacklisted in domain_lower:
            return True

    # Check against blacklisted extensions
    parsed = urlparse(domain)
    path = parsed.path.lower()
    for ext in BLACKLISTED_EXTENSIONS:
        if path.endswith(ext):
            return True

    return False


def load_domains(filename: str = DOMAINS_FILE) -> List[DomainTask]:
    """Load domains from CSV file.

    Expected CSV format: domain,email (optional)
    Example: example.com,contact@example.com
    """
    tasks = []
    path = Path(filename)

    if not path.exists():
        click.echo(f"⚠️  Archivo {filename} no encontrado. Creando archivo de ejemplo...")
        create_sample_domains_file(filename)
        return []

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith("#"):
                continue
            domain = row[0].strip()
            email = row[1].strip() if len(row) > 1 else ""
            if domain:
                # Skip blacklisted domains
                if is_domain_blacklisted(domain):
                    click.echo(f"⛏️ Dominio en blacklist omitido: {domain}")
                    continue
                tasks.append(DomainTask(domain, email))

    return tasks


def create_sample_domains_file(filename: str):
    """Create a sample domains.csv file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Domains to test - format: domain,email (optional)\n")
        f.write("example.com,contact@example.com\n")
        f.write("testsite.org\n")


def create_sample_smtp_accounts_file(filename: str = "smtp_accounts.csv"):
    """Create a sample smtp_accounts.csv file."""
    path = Path(filename)
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            f.write("# SMTP Accounts - Multiple accounts for rotation\n")
            f.write("# host,port,user,password,from_email\n")
            f.write("smtp.gmail.com,587,your-email@gmail.com,your-app-password,your-email@gmail.com\n")
        click.echo(f"✅ Archivo {filename} creado (plantilla)")


def create_sample_messages_file(filename: str = "messages.csv"):
    """Create a sample messages.csv file."""
    path = Path(filename)
    if not path.exists():
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["# Message templates for rotation"])
            writer.writerow(["name", "subject", "body"])
            writer.writerow(["default", "Hola", "Hola envié un mensaje desde el formulario web y no recibí respuesta. Quiero saber si recibieron mi mensaje."])
            writer.writerow(["followup", "Consulta sobre contacto", "Hola, les escribí hace unos días y quería hacer seguimiento de mi mensaje. Saludos."])
            writer.writerow(["new_contact", "Solicitud de información", "Hola, me interesa recibir más información sobre sus servicios. Por favor contactarme."])
        click.echo(f"✅ Archivo {filename} creado (plantilla)")


def create_sample_contacts_file(filename: str = "contacts.csv"):
    """Create a sample contacts.csv file."""
    path = Path(filename)
    if not path.exists():
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["# Contact data for form submission"])
            writer.writerow(["name", "email", "phone", "company", "subject", "message"])
            writer.writerow(["Juan Pérez", "juan.perez@email.com", "+54-9-11-1234-5678", "Empresa ABC", "Consulta", "Hola, me gustaría recibir información."])
            writer.writerow(["María García", "maria.garcia@email.com", "+54-9-11-8765-4321", "Compañía XYZ", "Solicitud", "Hola, envié un mensaje y no tuve respuesta."])
        click.echo(f"✅ Archivo {filename} creado (plantilla)")


def load_suppression_list(filename: str = SUPPRESSION_FILE) -> Set[str]:
    """Load suppressed email addresses from file."""
    suppressed = set()
    path = Path(filename)

    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and not row[0].startswith("#"):
                    suppressed.add(row[0].strip().lower())

    return suppressed


def add_to_suppression_list(email: str, reason: str, filename: str = SUPPRESSION_FILE):
    """Add an email to the suppression list."""
    path = Path(filename)
    file_exists = path.exists()

    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["email", "reason", "date_added"])
        writer.writerow([email.lower(), reason, datetime.now().isoformat()])


def log_result(
    domain: str,
    action: str,
    status: str,
    reason_code: str,
    details: str = "",
    evidence_path: str = "",
    filename: str = RESULTS_FILE,
):
    """Log a result to the results CSV file."""
    path = Path(filename)
    file_exists = path.exists()

    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp",
                "domain",
                "action",
                "status",
                "reason_code",
                "reason_description",
                "details",
                "evidence_path",
            ])
        writer.writerow([
            datetime.now().isoformat(),
            domain,
            action,
            status,
            reason_code,
            REASON_CODES.get(reason_code, reason_code),
            details,
            evidence_path,
        ])


# =============================================================================
# CRAWLER
# =============================================================================

class WebCrawler:
    """Crawls websites to find contact forms and email addresses."""

    def __init__(self, task: DomainTask):
        self.task = task
        self.base_url = self._normalize_url(task.domain)
        self.domain_hosts = {urlparse(self.base_url).netloc}
        self.last_request_time: Dict[str, float] = {}
        self.dynamic_pages_visited = 0

    def _normalize_url(self, domain: str) -> str:
        """Normalize domain to full URL."""
        if not domain.startswith(("http://", "https://")):
            return f"https://{domain}"
        return domain

    async def _rate_limited_request(self, client: httpx.AsyncClient, url: str) -> Optional[httpx.Response]:
        """Make a rate-limited HTTP request."""
        host = urlparse(url).netloc
        now = time.time()

        # Rate limiting
        if host in self.last_request_time:
            elapsed = now - self.last_request_time[host]
            if elapsed < RATE_LIMIT_DELAY:
                await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)

        for attempt in range(MAX_RETRIES):
            try:
                self.last_request_time[host] = time.time()
                response = await client.get(
                    url,
                    timeout=REQUEST_TIMEOUT,
                    follow_redirects=True,
                )
                return response
            except httpx.TimeoutException:
                if attempt == MAX_RETRIES - 1:
                    return None
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception:
                if attempt == MAX_RETRIES - 1:
                    return None
                await asyncio.sleep(2 ** attempt)

        return None

    async def crawl(self) -> Tuple[List[FormData], Set[str]]:
        """Crawl the domain for contact forms and emails."""
        forms_found = []
        emails_found = set()

        # Contador separado para páginas dinámicas descubiertas
        self.dynamic_pages_visited = 0
        max_dynamic_pages = MAX_PAGES_PER_DOMAIN  # 10 páginas

        # IP address to mask real IP (RFC 5737 documentation range)
        FAKE_IP = "203.0.113.1"

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            # Headers to mask real IP (some servers may respect these)
            "X-Forwarded-For": FAKE_IP,
            "X-Real-IP": FAKE_IP,
            "Forwarded": f"for={FAKE_IP}",
            "CF-Connecting-IP": FAKE_IP,
        }

        # Configure proxy if set
        proxy_config = None
        if PROXY_URL:
            proxy_config = PROXY_URL
        elif HTTP_PROXY or HTTPS_PROXY:
            proxy_config = {
                "http://": HTTP_PROXY or PROXY_URL,
                "https://": HTTPS_PROXY or PROXY_URL,
            }

        async with httpx.AsyncClient(headers=headers, proxy=proxy_config) as client:
            urls_to_visit = [self.base_url]

            # Agregar URLs de contacto comunes al inicio
            contact_urls = [
                "/contacto",
                "/contacto/",
                "/contact",
                "/contact/",
            ]
            base = self.base_url.rstrip('/')
            for contact_path in contact_urls:
                contact_url = f"{base}{contact_path}"
                if contact_url not in urls_to_visit:
                    urls_to_visit.append(contact_url)
                    click.echo(f"  📌 URL de contacto agregada: {contact_url}")

            while urls_to_visit:
                url = urls_to_visit.pop(0)

                if url in self.task.visited_urls:
                    continue

                # Verificar si es una URL predefinida o dinámica
                is_predefined = any(url.endswith(path) or url.rstrip('/').endswith(path.rstrip('/'))
                                    for path in ["/contacto", "/contact"])
                # La homepage (URL base) se considera seed, no dinámica
                is_seed = url.rstrip('/') == self.base_url.rstrip('/')

                # Si es dinámica y ya alcanzamos el límite, saltar
                if not is_predefined and not is_seed and self.dynamic_pages_visited >= max_dynamic_pages:
                    continue

                self.task.visited_urls.add(url)
                if not is_predefined and not is_seed:
                    self.dynamic_pages_visited += 1

                click.echo(f"  🔍 Crawling: {url}")

                response = await self._rate_limited_request(client, url)
                if not response:
                    click.echo(f"     ⚠️  [DIAG] No response received from {url}")
                    continue
                if response.status_code != 200:
                    click.echo(f"     ⚠️  [DIAG] HTTP {response.status_code} for {url}")
                    continue

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    click.echo(f"     ⚠️  [DIAG] Content-Type '{content_type}' not HTML for {url}")
                    continue

                # Parse HTML - manejo manual de compresión
                # Algunos servidores envían gzip sin marcar Content-Encoding correctamente
                content_bytes = response.content

                # Detectar y descomprimir contenido si es necesario
                if content_bytes[:2] == b'\x1f\x8b':  # Magic bytes gzip
                    click.echo(f"     📦 Descomprimiendo gzip...")
                    try:
                        import gzip
                        content_bytes = gzip.decompress(content_bytes)
                    except Exception as e:
                        click.echo(f"     ⚠️  Error al descomprimir gzip: {e}")
                elif content_bytes[:4] == b'\x04\x22\x4d\x18':  # Magic bytes brotli
                    click.echo(f"     📦 Descomprimiendo brotli...")
                    try:
                        import brotli
                        content_bytes = brotli.decompress(content_bytes)
                    except Exception as e:
                        click.echo(f"     ⚠️  Error al descomprimir brotli: {e}")

                # Decodificar a string
                try:
                    html_content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    html_content = content_bytes.decode('utf-8', errors='replace')

                html_size = len(html_content)
                click.echo(f"     [DEBUG] HTML size: {html_size} bytes")

                if html_size < 100:
                    click.echo(f"     ⚠️  HTML muy pequeño, posiblemente página vacía o redirección")
                    continue

                # Debug: ver primeros 500 caracteres del HTML
                click.echo(f"     [DEBUG] HTML preview: {html_content[:500]}")

                soup = BeautifulSoup(html_content, 'html.parser')

                # Debug: verificar que BeautifulSoup funcionó
                click.echo(f"     [DEBUG] BeautifulSoup object type: {type(soup)}")
                click.echo(f"     [DEBUG] HTML title: {soup.title.string if soup.title else 'No title'}")

                # Look for contact forms
                page_forms = self._extract_forms(soup, url, html_content)
                forms_found.extend(page_forms)

                # Look for emails
                page_emails = self._extract_emails(soup, html_content)
                emails_found.update(page_emails)

                # Find links to follow
                new_urls = self._extract_links(soup, url, html_content)
                click.echo(f"     [DIAG] Total enlaces extraídos de {url}: {len(new_urls)}")
                if new_urls:
                    click.echo(f"     ↳ Enlaces encontrados: {len(new_urls)}")
                    for i, new_url in enumerate(new_urls[:5]):  # Show first 5
                        click.echo(f"       - {new_url}")
                    if len(new_urls) > 5:
                        click.echo(f"       ... y {len(new_urls) - 5} más")
                else:
                    click.echo(f"     ⚠️  No se encontraron enlaces en {url}")

                # Track URL filtering
                added_count = 0
                skipped_already_visited = 0
                skipped_already_queued = 0

                for new_url in new_urls:
                    if new_url in self.task.visited_urls:
                        skipped_already_visited += 1
                        continue
                    if new_url in urls_to_visit:
                        skipped_already_queued += 1
                        continue

                    if self._is_contact_page(new_url):
                        urls_to_visit.insert(0, new_url)  # Prioritize contact pages
                        added_count += 1
                        click.echo(f"     [DIAG] Agregada URL de contacto: {new_url}")
                    else:
                        urls_to_visit.append(new_url)
                        added_count += 1
                        click.echo(f"     [DIAG] Agregada URL dinámica: {new_url}")

                if skipped_already_visited > 0:
                    click.echo(f"     [DIAG] URLs saltadas (ya visitadas): {skipped_already_visited}")
                if skipped_already_queued > 0:
                    click.echo(f"     [DIAG] URLs saltadas (ya en cola): {skipped_already_queued}")
                if added_count > 0:
                    click.echo(f"     ↳ URLs agregadas a la cola: {added_count} (total en cola: {len(urls_to_visit)})")
                else:
                    click.echo(f"     [DIAG] Ninguna URL nueva agregada desde {url}")

        # Hybrid crawling: if no forms found with static crawler, try Playwright
        if not forms_found:
            click.echo(f"  🔍 No se encontraron formularios con crawling estático, intentando crawling híbrido...")
            # Get contact page URLs from visited URLs
            contact_urls = [url for url in self.task.visited_urls if self._is_contact_page(url)]
            if not contact_urls:
                contact_urls = [url for url in self.task.visited_urls][:5]  # Use first 5 URLs
            pw_forms, pw_emails = await self.crawl_with_playwright(contact_urls)
            if pw_forms:
                click.echo(f"  ✅ Formularios encontrados con crawling híbrido: {len(pw_forms)}")
                forms_found.extend(pw_forms)
            if pw_emails:
                click.echo(f"  ✅ Emails adicionales encontrados: {len(pw_emails)}")
                emails_found.update(pw_emails)

        return forms_found, emails_found

    def _extract_forms(self, soup: BeautifulSoup, url: str, html: str) -> List[FormData]:
        """Extract contact forms from the page."""
        forms = []

        for form_node in soup.find_all("form"):
            form_html = str(form_node)
            fields = {}
            submit_button = None
            all_inputs = []  # Para debugging

            # Extract ALL input fields (incluyendo ocultos para mejor detección)
            for input_node in form_node.find_all(["input", "textarea", "select"]):
                input_type = input_node.get("type", "text").lower()
                input_name = input_node.get("name", "")
                input_id = input_node.get("id", "")
                placeholder = input_node.get("placeholder", "").lower()

                # Buscar label asociado al campo
                label_text = self._find_field_label(soup, input_id, input_name)

                all_inputs.append({
                    "type": input_type,
                    "name": input_name,
                    "id": input_id,
                    "placeholder": placeholder,
                    "label": label_text,
                })

                # Skip submit/button inputs para el mapeo de campos
                if input_type in ("submit", "button", "image"):
                    if input_type == "submit":
                        submit_button = input_name or input_id
                    continue

                # Map field to known types (incluyendo campos ocultos)
                field_key = self._classify_field(input_name, input_id, placeholder, label_text, input_type)
                if field_key:
                    fields[field_key] = {
                        "name": input_name,
                        "id": input_id,
                        "type": input_type,
                        "placeholder": placeholder,
                    }

            # Check if this looks like a contact form
            # Criterio: debe tener campo email + (mensaje O nombre)
            has_email = "email" in fields
            has_message = "message" in fields
            has_name = "name" in fields

            if has_email and (has_message or has_name):
                form_data = FormData(url, form_html, fields, submit_button)

                # Check for CAPTCHA (limit to form node to avoid false positives)
                has_captcha, captcha_type = self._has_captcha(form_node, html)
                if has_captcha:
                    form_data.has_captcha = True
                    form_data.captcha_type = captcha_type

                # Check for honeypot
                if self._has_honeypot(form_node):
                    click.echo(f"        ⚠️  Honeypot detectado, pero se procesará de todos modos")
                    form_data.has_honeypot = True

                forms.append(form_data)
            elif has_email:
                # Debug: mostrar por qué no se detectó como formulario de contacto
                click.echo(f"     ℹ️  Formulario con email encontrado pero sin message/name: {url}")
                click.echo(f"        Campos detectados: {list(fields.keys())}")

        return forms

    def _find_field_label(self, soup: BeautifulSoup, field_id: str, field_name: str) -> str:
        """Find label text associated with a field."""
        label_text = ""

        if field_id:
            # Buscar label con atributo for
            label_node = soup.find("label", attrs={"for": field_id})
            if label_node:
                label_text = label_node.get_text(strip=True).lower()

        if not label_text and field_name:
            # Buscar label con atributo for por name
            label_node = soup.find("label", attrs={"for": field_name})
            if label_node:
                label_text = label_node.get_text(strip=True).lower()

        return label_text

    def _classify_field(self, name: str, field_id: str, placeholder: str, label_text: str = "", input_type: str = "") -> Optional[str]:
        """Classify a form field based on its attributes and label.

        Handles complex field naming patterns like:
        - Array notation: form_fields[email], fields[name], etc.
        - Prefixed fields: field_email, field_name, etc.
        - Elementor-style: form_fields[email], form_fields[message], etc.
        """
        search_text = f"{name} {field_id} {placeholder} {label_text}".lower()

        # Handle array notation like form_fields[email], fields[name], etc.
        # Extract the inner part from brackets
        import re
        array_matches = re.findall(r'\[([^\]]+)\]', name.lower())
        if array_matches:
            # Add the extracted names to search text
            search_text += " " + " ".join(array_matches)

        # Handle prefixed field names like field_email, input_name, etc.
        # Split by underscore and add components
        if "_" in name:
            name_parts = name.lower().split("_")
            search_text += " " + " ".join(name_parts)

        for field_type, keywords in FORM_FIELD_MAPPINGS.items():
            for keyword in keywords:
                if keyword in search_text:
                    return field_type

        # Heurísticas adicionales para campos comunes
        # Si tiene type="email", es probablemente email
        if "email" in search_text or "correo" in search_text or "e-mail" in search_text:
            return "email"

        # Si parece un campo de asunto pero no se detectó antes
        if any(word in search_text for word in ["asunto", "subject", "tema", "motivo"]):
            return "subject"

        # Si parece un campo de teléfono
        if any(word in search_text for word in ["phone", "telefono", "tel", "mobile", "celular"]):
            return "phone"

        return None

    def _has_captcha(self, form_node, html: str = "") -> Tuple[bool, str]:
        """Check if the form has CAPTCHA protection.

        Looks specifically within the form node to avoid false positives from
        global scripts loaded elsewhere on the page.

        Returns: (has_captcha, captcha_type)
        """
        form_html = str(form_node).lower()

        # Check for explicit CAPTCHA containers within the form
        captcha_selectors = [
            '.g-recaptcha',  # reCAPTCHA v2
            '[data-sitekey]',  # Generic CAPTCHA with sitekey
            '.h-captcha',  # hCAPTCHA
            '.recaptcha',
            '#recaptcha',
            'iframe[src*="recaptcha"]',  # reCAPTCHA iframe
            'iframe[src*="hcaptcha"]',  # hCAPTCHA iframe
        ]

        for selector in captcha_selectors:
            if form_node.select_one(selector):
                if 'recaptcha' in selector or 'data-sitekey' in selector:
                    return True, "reCAPTCHA"
                elif 'hcaptcha' in selector:
                    return True, "hCAPTCHA"

        # Check for input fields that indicate CAPTCHA
        captcha_inputs = form_node.find_all("input", {"name": lambda x: x and "captcha" in x.lower()})
        if captcha_inputs:
            return True, "CAPTCHA"

        # Check for reCAPTCHA v3 (invisible) - this loads globally but we check if
        # it's specifically bound to this form via data-action or nearby script
        form_scripts = form_node.find_all("script")
        for script in form_scripts:
            script_text = str(script).lower()
            if 'recaptcha' in script_text or 'grecaptcha' in script_text:
                return True, "reCAPTCHA"

        # Check for specific CAPTCHA text/labels within the form
        form_text = form_node.get_text(strip=True).lower()
        explicit_captcha_indicators = [
            "i'm not a robot",
            "no soy un robot",
            "verify you're human",
            "security check",
            "security code",
            "código de seguridad",
        ]
        for indicator in explicit_captcha_indicators:
            if indicator in form_text:
                return True, "CAPTCHA"

        # Check for visible CAPTCHA input fields (user needs to type)
        captcha_inputs_visible = form_node.find_all(
            "input",
            {"type": "text", "name": lambda x: x and any(word in x.lower() for word in ["captcha", "security", "verification"])}
        )
        if captcha_inputs_visible:
            return True, "CAPTCHA"

        return False, ""

    def _has_honeypot(self, form_node) -> bool:
        """Check if the form has a honeypot field.

        Honeypots are fields designed to trick bots. They are typically:
        - Fields hidden from users (display:none, visibility:hidden, off-screen)
        - Fields with names that sound legitimate but are actually traps
        """
        # Contar campos visibles vs ocultos
        visible_fields = 0
        hidden_fields = 0
        honeypot_indicators = 0

        for input_node in form_node.find_all("input"):
            input_type = input_node.get("type", "").lower()
            input_name = input_node.get("name", "").lower()
            style = input_node.get("style", "").lower()

            # Saltar campos de tipo submit, button, image
            if input_type in ("submit", "button", "image"):
                continue

            # Verificar si es un campo oculto
            is_hidden = input_type == "hidden"
            is_css_hidden = "display:none" in style or "visibility:hidden" in style
            is_off_screen = "left:-" in style or "top:-" in style

            if is_hidden or is_css_hidden or is_off_screen:
                hidden_fields += 1

                # Solo marcar como honeypot si el campo oculto tiene nombre sospechoso
                # y NO hay otros campos legítimos visibles en el formulario
                honeypot_names = ["email", "name", "phone", "url", "website", "company"]
                if any(keyword in input_name for keyword in honeypot_names):
                    # Verificar si tiene prefijos/sufijos típicos de honeypot
                    if any(indicator in input_name for indicator in [
                        "trap", "honeypot", "bot", "spam", "sneaky",
                        "_chk", "check", "verify", "validation"
                    ]):
                        honeypot_indicators += 1
            else:
                visible_fields += 1

        # Es honeypot si hay indicadores fuertes de honeypot
        # O si hay campos ocultos sospechosos sin campos visibles
        if honeypot_indicators > 0:
            return True

        # No es honeypot si hay campos visibles (formulario legítimo)
        if visible_fields > 0:
            return False

        # Solo campos ocultos = probable honeypot
        return hidden_fields > 0 and visible_fields == 0

    async def crawl_with_playwright(self, urls: List[str]) -> Tuple[List[FormData], Set[str]]:
        """Crawl URLs using Playwright to find JavaScript-rendered forms.

        This is used as a fallback when static crawling doesn't find forms.
        It renders pages with a headless browser, allowing JavaScript to execute.
        """
        forms_found = []
        emails_found = set()

        if not urls:
            return forms_found, emails_found

        click.echo(f"  🔍 Iniciando crawling híbrido con Playwright para {len(urls)} URLs...")

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                # Configure context with same headers as regular crawler
                FAKE_IP = "203.0.113.1"
                context_options = {
                    "user_agent": USER_AGENT,
                    "viewport": {"width": 1280, "height": 720},
                    "extra_http_headers": {
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                        "X-Forwarded-For": FAKE_IP,
                        "X-Real-IP": FAKE_IP,
                        "Forwarded": f"for={FAKE_IP}",
                        "CF-Connecting-IP": FAKE_IP,
                    },
                }

                context = await browser.new_context(**context_options)
                page = await context.new_page()

                for url in urls[:3]:  # Limit to first 3 URLs for performance
                    try:
                        click.echo(f"    🔍 Renderizando: {url}")
                        response = await page.goto(url, wait_until="networkidle", timeout=30000)

                        if not response or response.status >= 400:
                            continue

                        # Wait for forms to potentially load
                        await asyncio.sleep(2)

                        # Get page content after JavaScript execution
                        html_content = await page.content()
                        soup = BeautifulSoup(html_content, 'html.parser')

                        # Look for forms
                        page_forms = self._extract_forms(soup, url, html_content)
                        if page_forms:
                            click.echo(f"    ✅ Formularios encontrados con Playwright: {len(page_forms)}")
                            forms_found.extend(page_forms)

                        # Look for emails
                        page_emails = self._extract_emails(soup, html_content)
                        emails_found.update(page_emails)

                        # Look for iframes containing forms (HubSpot, Typeform, etc.)
                        iframes = await page.query_selector_all("iframe")
                        for i, iframe in enumerate(iframes):
                            try:
                                frame = await iframe.content_frame()
                                if frame:
                                    frame_html = await frame.content()
                                    frame_soup = BeautifulSoup(frame_html, 'html.parser')
                                    frame_forms = self._extract_forms(frame_soup, url, frame_html)
                                    if frame_forms:
                                        click.echo(f"    ✅ Formulario encontrado en iframe {i+1}")
                                        forms_found.extend(frame_forms)
                            except Exception as e:
                                click.echo(f"    ⚠️ Error al inspeccionar iframe: {e}")

                    except Exception as e:
                        click.echo(f"    ⚠️ Error al renderizar {url}: {e}")

                await browser.close()

        except Exception as e:
            click.echo(f"  ⚠️ Error en crawling híbrido: {e}")

        return forms_found, emails_found

    def _extract_emails(self, soup: BeautifulSoup, html: str) -> Set[str]:
        """Extract email addresses from the page."""
        emails = set()

        # Look for mailto: links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("mailto:"):
                email = href[7:].split("?")[0].strip()
                if self._is_valid_email(email):
                    emails.add(email.lower())

        # Look for email patterns in text
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, html)
        for email in matches:
            if self._is_valid_email(email):
                emails.add(email.lower())

        return emails

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        return bool(re.match(pattern, email))

    def _extract_links(self, soup: BeautifulSoup, base_url: str, html: str = "") -> List[str]:
        """Extract internal links from the page."""
        links = []
        seen = set()  # Evitar duplicados
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc

        # Find all links
        all_links = soup.find_all("a", href=True)
        click.echo(f"     [DEBUG] Total <a> tags: {len(soup.find_all('a'))}, con href: {len(all_links)}")

        for link in all_links:
            try:
                href = link["href"].strip()

                if not href:
                    continue

                # Skip anchors and special links
                if href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
                    continue

                # Resolve relative URLs
                full_url = urljoin(base_url, href)
                parsed = urlparse(full_url)

                # Only same domain links (normalize by removing www. prefix)
                normalized_link_domain = parsed.netloc.removeprefix("www.")
                normalized_base_domain = base_domain.removeprefix("www.")
                if normalized_link_domain != normalized_base_domain:
                    click.echo(f"     [DIAG-LINK] Filtrado por dominio diferente: '{parsed.netloc}' != '{base_domain}'")
                    continue

                # Normalize URL (remove fragments)
                full_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    full_url += f"?{parsed.query}"

                # Avoid duplicates and current URL
                normalized = full_url.rstrip('/')
                if normalized not in seen and normalized != base_url.rstrip('/'):
                    seen.add(normalized)
                    links.append(full_url)
            except Exception as e:
                continue

        # Debug: summary of filtering
        click.echo(f"     [DIAG-LINK] Resumen: base_domain='{base_domain}', enlaces internos={len(links)}")

        # Debug: show some found links
        if links:
            click.echo(f"     [DEBUG] Enlaces internos encontrados: {len(links)}")
            for i, link in enumerate(links[:3]):
                click.echo(f"       - {link}")
        else:
            click.echo(f"     [DEBUG] No se encontraron enlaces internos")

        return links

    def _is_contact_page(self, text: str) -> bool:
        """Check if URL or text looks like a contact page."""
        contact_keywords = [
            "contact", "contacto", "kontakt", "contactenos",
            "reach-us", "get-in-touch", "write-us", "escribenos",
            "help", "support", "ayuda", "soporte",
            "about", "nosotros", "about-us", "acerca"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in contact_keywords)


# =============================================================================
# SMTP MODULE
# =============================================================================

class SMTPSender:
    """Sends emails via SMTP with bounce handling and account rotation."""

    def __init__(self, browser=None):
        self.browser = browser
        self._load_account()

    def _load_account(self):
        """Load next SMTP account from library."""
        account = message_lib.get_next_smtp_account()
        self.host = account["host"]
        self.port = account["port"]
        self.user = account["user"]
        self.password = account["password"]
        self.from_email = account["from_email"]

    async def send_email(self, to_email: str, subject: str = "", body: str = "") -> Tuple[bool, str]:
        """Send an email via SMTP using library account."""
        # Reload account on each send for rotation
        self._load_account()

        if not all([self.host, self.user, self.password]):
            return False, "SMTP credentials not configured"

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Get template from library
            template = message_lib.get_next_message_template()
            contact = message_lib.get_next_contact_data()

            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject or template["subject"]

            # Use body from template with contact data substitution
            body_text = body or template["body"]
            # Replace placeholders
            body_text = body_text.replace("{name}", contact.get("name", ""))
            body_text = body_text.replace("{email}", contact.get("email", ""))
            body_text = body_text.replace("{phone}", contact.get("phone", ""))
            body_text = body_text.replace("{company}", contact.get("company", ""))
            msg.attach(MIMEText(body_text, "plain"))

            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)

            click.echo(f"     📧 Enviado desde: {self.from_email}")
            return True, "Email sent successfully"

        except smtplib.SMTPRecipientsRefused as e:
            return False, f"Hard bounce: {str(e)}"
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Unknown error: {str(e)}"


# =============================================================================
# FORM SUBMITTER (Playwright)
# =============================================================================

class FormSubmitter:
    """Submits forms using Playwright for JavaScript support."""

    def __init__(self, browser=None):
        self.browser = browser
        self.evidence_dir = Path(EVIDENCE_DIR)
        self.evidence_dir.mkdir(exist_ok=True)

    async def _dismiss_popups(self, page):
        """Dismiss common popups, cookie banners, and modals before form interaction.

        This handles GDPR cookie banners, newsletter signup modals, chat widgets,
        and other overlays that might block form interaction.
        """
        popup_selectors = [
            # Cookie consent buttons
            "button[aria-label*='cookie' i]",
            "button[aria-label*='accept' i]",
            ".cookie-accept",
            ".accept-cookies",
            "#accept-cookies",
            "[data-testid='cookie-accept']",
            "button:has-text('Accept')",
            "button:has-text('Aceptar')",
            "button:has-text('Accept all')",
            "button:has-text('Aceptar todo')",
            "button:has-text('OK')",
            "button:has-text('Entendido')",
            "button:has-text('Agree')",
            "button:has-text('Consent')",
            "button:has-text('Allow')",
            "button:has-text('Permitir')",
            ".cc-accept",
            ".cc-allow",
            "#onetrust-accept-btn-handler",
            ".ot-sdk-show-settings",
            "[class*='cookie-banner'] button:first-of-type",
            "[class*='gdpr'] button:first-of-type",
            # Close buttons for modals
            "button.close",
            ".modal-close",
            ".popup-close",
            "[aria-label='Close']",
            "[data-dismiss='modal']",
            ".fancybox-close",
            ".mfp-close",
            # Newsletter signup close
            ".newsletter-close",
            ".signup-close",
            "button:has-text('No thanks')",
            "button:has-text('No, gracias')",
            "button:has-text('Later')",
            "button:has-text('Cerrar')",
        ]

        for selector in popup_selectors:
            try:
                # Try to click the element with a short timeout
                element = await page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        await element.click(timeout=1000)
                        click.echo(f"        ✅ Popup/cookie banner dismissed: {selector}")
                        await asyncio.sleep(0.5)  # Wait for animation
            except Exception:
                # Silently continue if selector not found or click fails
                continue

    async def _handle_mandatory_checkboxes(self, page):
        """Find and check mandatory checkboxes for Terms, Privacy Policy, etc.

        Many forms require accepting terms and privacy policy before submission.
        This method identifies these checkboxes and checks them.
        """
        checkbox_selectors = [
            # Terms and conditions
            "input[type='checkbox'][name*='terms']",
            "input[type='checkbox'][name*='terminos']",
            "input[type='checkbox'][name*='conditions']",
            "input[type='checkbox'][name*='condiciones']",
            # Privacy policy
            "input[type='checkbox'][name*='privacy']",
            "input[type='checkbox'][name*='privacidad']",
            "input[type='checkbox'][name*='policy']",
            "input[type='checkbox'][name*='politica']",
            # Required checkboxes
            "input[type='checkbox'][required]",
            "input[type='checkbox'][aria-required='true']",
            # GDPR consent
            "input[type='checkbox'][name*='consent']",
            "input[type='checkbox'][name*='consentimiento']",
            "input[type='checkbox'][name*='gdpr']",
            "input[type='checkbox'][name*='dsgvo']",
            # Accept/Agree checkboxes
            "input[type='checkbox'][name*='accept']",
            "input[type='checkbox'][name*='acept']",
            "input[type='checkbox'][name*='agree']",
            # Labels containing these keywords
            "label:has-text('terms') input[type='checkbox']",
            "label:has-text('privacy') input[type='checkbox']",
            "label:has-text('términos') input[type='checkbox']",
            "label:has-text('privacidad') input[type='checkbox']",
            "label:has-text('política') input[type='checkbox']",
            "label:has-text('conditions') input[type='checkbox']",
            "label:has-text('condiciones') input[type='checkbox']",
        ]

        checked_count = 0
        for selector in checkbox_selectors:
            try:
                # Check if checkbox exists and is not already checked
                checkboxes = await page.query_selector_all(selector)
                for checkbox in checkboxes:
                    try:
                        # Check if checkbox is visible and not already checked
                        is_visible = await checkbox.is_visible()
                        is_checked = await checkbox.is_checked()
                        if is_visible and not is_checked:
                            # Check the checkbox
                            await checkbox.check()
                            checked_count += 1
                            click.echo(f"        ✅ Checked mandatory checkbox: {selector}")
                    except Exception as e:
                        click.echo(f"        ⚠️ Error checking checkbox: {e}")
            except:
                continue

        if checked_count > 0:
            click.echo(f"        ✅ Total mandatory checkboxes checked: {checked_count}")

    async def submit_form(self, form: FormData) -> Tuple[bool, str, str]:
        """Submit a form using Playwright with proper validation."""
        evidence_path = ""
        unfilled_fields = []

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                # Configure proxy for Playwright if set
                proxy_config = None
                if PROXY_URL:
                    proxy_config = {"server": PROXY_URL}
                elif HTTP_PROXY:
                    proxy_config = {"server": HTTP_PROXY}

                browser = await p.chromium.launch(headless=True)

                # IP address to mask real IP
                FAKE_IP = "203.0.113.1"

                context_options = {
                    "user_agent": USER_AGENT,
                    "viewport": {"width": 1280, "height": 720},
                    "extra_http_headers": {
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                        "Upgrade-Insecure-Requests": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-User": "?1",
                        "X-Forwarded-For": FAKE_IP,
                        "X-Real-IP": FAKE_IP,
                        "Forwarded": f"for={FAKE_IP}",
                        "CF-Connecting-IP": FAKE_IP,
                    },
                }

                if proxy_config:
                    context_options["proxy"] = proxy_config

                context = await browser.new_context(**context_options)
                page = await context.new_page()

                # Set up network interception to detect AJAX responses
                network_responses = []
                async def handle_response(response):
                    """Capture network responses to detect successful AJAX submissions."""
                    try:
                        url = response.url
                        status = response.status
                        # Check for common contact form API endpoints
                        api_patterns = [
                            "/wp-json/", "/api/", "/contact", "/form",
                            "wpcf7", "ajax", "submit", "send", "contact-form-7",
                            "/wp-admin/admin-ajax.php",
                        ]
                        if any(pattern in url.lower() for pattern in api_patterns):
                            network_responses.append({
                                "url": url,
                                "status": status,
                                "success": 200 <= status < 300,
                            })
                            click.echo(f"        🌐 API call detected: {url} (status: {status})")
                    except:
                        pass

                page.on("response", handle_response)

                # Navigate to the form page
                response = await page.goto(form.url, wait_until="networkidle", timeout=30000)

                # Check if page loaded successfully
                if response and response.status >= 400:
                    await browser.close()
                    return False, f"HTTP_ERROR: Page returned status {response.status}", ""

                # Dismiss popups and cookie banners before interacting with the form
                await self._dismiss_popups(page)

                # Fill in form fields
                for field_type, field_info in form.fields.items():
                    value = TEST_DATA.get(field_type, "")
                    if value:
                        # Probar múltiples selectores mejorados
                        selectors = [
                            f"[name='{field_info['name']}']",
                            f"#{field_info['id']}",
                            f"input[name*='{field_info['name']}']",
                            f"textarea[name*='{field_info['name']}']",
                            f"input[placeholder*='{field_info['name']}']",
                            f"textarea[placeholder*='{field_info['name']}']",
                            f"input[type='{field_info['type']}']",
                        ]
                        filled = False
                        for selector in selectors:
                            try:
                                # Check if element exists and is visible
                                element = await page.query_selector(selector)
                                if element:
                                    is_visible = await element.is_visible()
                                    if is_visible:
                                        await page.fill(selector, value)
                                        filled = True
                                        break
                            except:
                                continue
                        if not filled:
                            unfilled_fields.append(field_type)
                            if field_type in ["email", "message"]:
                                click.echo(f"        ⚠️  No se pudo llenar campo CRÍTICO {field_type}")
                            else:
                                click.echo(f"        ℹ️  Campo opcional {field_type} no encontrado, continuando...")

                # Check if critical fields were not filled
                critical_fields = ["email", "message"]
                missing_critical = [f for f in critical_fields if f in form.fields and f in unfilled_fields]
                if missing_critical:
                    await browser.close()
                    return False, f"FORM_FILL_ERROR: Could not fill critical fields: {', '.join(missing_critical)}", ""

                # Log optional fields that were skipped
                optional_unfilled = [f for f in unfilled_fields if f not in critical_fields]
                if optional_unfilled:
                    click.echo(f"        ℹ️  Campos opcionales omitidos: {', '.join(optional_unfilled)}")

                # Check and accept mandatory checkboxes (T&C, Privacy Policy, etc.)
                await self._handle_mandatory_checkboxes(page)

                # Prepare log file path for this form submission
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                domain = urlparse(form.url).netloc.replace(".", "_")
                log_filename = f"{domain}_{timestamp}.log"
                log_path = self.evidence_dir / log_filename
                evidence_path = str(log_path)

                # Submit the form
                submit_clicked = False
                if form.submit_button:
                    try:
                        # Scroll into view and click with force to handle overlays
                        await page.locator(f"[name='{form.submit_button}']").scroll_into_view_if_needed(timeout=2000)
                        await page.click(f"[name='{form.submit_button}'", force=True)
                        submit_clicked = True
                    except Exception as e:
                        click.echo(f"        ⚠️ Error clicking named submit button: {e}")
                        # Try fallback without force
                        try:
                            await page.click(f"[name='{form.submit_button}']", timeout=2000)
                            submit_clicked = True
                        except:
                            pass

                if not submit_clicked:
                    # Try to find submit button with improved selectors
                    submit_selectors = [
                        "button[type='submit']",
                        "input[type='submit']",
                        "button:has-text('Send')",
                        "button:has-text('Submit')",
                        "button:has-text('Enviar')",
                        "button:has-text('Enviar mensaje')",
                        "button:has-text('Contactar')",
                        "button:has-text('Enviar correo')",
                        "input[value*='Enviar']",
                        "input[value*='Send']",
                        "input[value*='Submit']",
                        "[class*='submit']",
                        "[class*='send']",
                        "button[class*='btn']",
                    ]
                    for selector in submit_selectors:
                        try:
                            # Scroll into view first
                            await page.locator(selector).scroll_into_view_if_needed(timeout=1000)
                            # Try force click first
                            await page.click(selector, force=True, timeout=2000)
                            submit_clicked = True
                            click.echo(f"        ✅ Form submitted using: {selector}")
                            break
                        except:
                            # Try normal click as fallback
                            try:
                                await page.click(selector, timeout=2000)
                                submit_clicked = True
                                click.echo(f"        ✅ Form submitted using: {selector}")
                                break
                            except:
                                continue

                if not submit_clicked:
                    await browser.close()
                    return False, "FORM_SUBMIT_ERROR: Could not find or click submit button", evidence_path

                # Wait for response with multiple strategies
                # Para WordPress/Contact Form 7, esperar respuesta AJAX
                try:
                    # Intentar detectar respuesta AJAX de Contact Form 7
                    await page.wait_for_selector(".wpcf7-response-output", timeout=10000)
                except:
                    # Si no es CF7, esperar carga normal
                    try:
                        await page.wait_for_load_state("networkidle", timeout=10000)
                    except:
                        # Networkidle might not fire, wait for timeout or domcontentloaded
                        try:
                            await page.wait_for_load_state("domcontentloaded", timeout=5000)
                        except:
                            pass

                # Esperar un poco más para AJAX
                await asyncio.sleep(2)

                # Validate submission result with network responses
                validation_result = await self._validate_submission(page, network_responses)

                await browser.close()

                if validation_result["success"]:
                    return True, "FORM_SUBMITTED_SUCCESS", evidence_path
                else:
                    return False, f"FORM_VALIDATION_FAILED: {validation_result['reason']}", evidence_path

        except Exception as e:
            return False, f"UNKNOWN_ERROR: {str(e)}", evidence_path

    async def _validate_submission(self, page, network_responses: List[Dict] = None) -> dict:
        """Validate if the form submission was successful by checking page content."""
        try:
            # Get page content and URL
            content = await page.content()
            content_lower = content.lower()
            url = page.url

            # Success indicators in multiple languages
            success_indicators = [
                "gracias", "thank you", "thanks", "merci", "grazie",
                "mensaje enviado", "message sent", "sent successfully",
                "enviado correctamente", "sent successfully",
                "mensaje recibido", "message received",
                "contacto recibido", "contact received",
                "success", "éxito", "succès", "successo",
                "confirmación", "confirmation",
                "nos pondremos en contacto", "we will contact you",
                "respuesta enviada", "response submitted",
                # Contact Form 7 específico
                "wpcf7-mail-sent-ok",
                # Elementor específico
                "elementor-message-success",
                "form submitted successfully",
            ]

            # Server/Technical error indicators - específicos para errores reales
            error_indicators = [
                # Errores HTTP explícitos
                "http error", "server error", "internal server error",
                "bad request", "forbidden", "unauthorized",
                # Errores de envío específicos
                "failed to send", "no se pudo enviar", "could not send",
                "message failed", "el mensaje no se pudo enviar",
                "envío fallido", "submission failed",
                # Errores de validación de servidor
                "validation failed", "invalid submission",
                "spam detected", "blocked",
            ]

            # Field validation indicators - estos son solo validaciones, no errores del servidor
            field_validation_indicators = [
                "required", "requerido", "obligatorio", "requis",
                "por favor complete", "please fill",
                "campo vacío", "empty field", "missing", "falta", "manquant",
            ]

            # Check for success indicators
            found_success = any(indicator in content_lower for indicator in success_indicators)

            # Check for server/technical errors (solo errores específicos, no la palabra "error" sola)
            found_error = any(indicator in content_lower for indicator in error_indicators)

            # Check for field validation messages
            found_field_validation = any(indicator in content_lower for indicator in field_validation_indicators)

            # Check for form still present (might indicate submission failed)
            form_still_present = await page.query_selector("form") is not None

                # Check for successful AJAX API calls first (most reliable for SPAs)
            if network_responses:
                successful_api_calls = [r for r in network_responses if r.get("success")]
                if successful_api_calls:
                    # Check if any of these are contact form submissions
                    for response in successful_api_calls:
                        url = response.get("url", "").lower()
                        if any(pattern in url for pattern in ["contact", "form", "wpcf7", "submit", "send"]):
                            return {"success": True, "reason": f"Successful API call detected: {response['url']}"}

            # Check for toast notifications (common in SPAs)
            toast_selectors = [
                ".toast",
                ".notification",
                ".alert-success",
                ".success-message",
                ".message-success",
                "[class*='toast']",
                "[class*='notification']",
                "[class*='success']",
            ]
            for selector in toast_selectors:
                try:
                    toast = await page.query_selector(selector)
                    if toast:
                        toast_text = await toast.text_content()
                        if toast_text and any(word in toast_text.lower() for word in ["success", "sent", "enviado", "gracias", "thank"]):
                            return {"success": True, "reason": f"Success toast detected: {toast_text[:50]}"}
                except:
                    pass

            # Analyze result
            if found_error and not found_success:
                return {"success": False, "reason": "Error messages detected on page"}

            # Si hay validación de campo pero no error del servidor, podría ser por campos opcionales faltantes
            # Intentar continuar si no hay error técnico grave
            if found_field_validation and not found_success and not found_error:
                # Si el formulario ya no está presente, probablemente se envió
                if not form_still_present:
                    return {"success": True, "reason": "Form submitted (field validation messages may indicate optional fields)"}

            if found_success:
                return {"success": True, "reason": "Success message detected"}

            # If URL changed (redirected), likely successful
            # but we can't be 100% sure without more context

            # If no clear indicators, be conservative
            if not found_success and not found_error:
                # Check if we're on a thank-you or confirmation page
                if any(word in url.lower() for word in ["thank", "gracias", "confirm", "success"]):
                    return {"success": True, "reason": "Redirected to success/confirmation page"}

                # If form is still there and no success message, likely failed
                if form_still_present:
                    return {"success": False, "reason": "Form still present, no success confirmation detected"}

                # Ambiguous case - form gone but no confirmation
                return {"success": False, "reason": "No success confirmation detected after submission"}

            return {"success": found_success, "reason": "Based on page content analysis"}

        except Exception as e:
            return {"success": False, "reason": f"Validation error: {str(e)}"}


# =============================================================================
# MAIN PROCESSING
# =============================================================================

class FormTester:
    """Main class for processing domains."""

    def __init__(self, browser=None):
        self.browser = browser
        self.smtp_sender = SMTPSender()
        self.form_submitter = FormSubmitter()
        self.suppression_list = load_suppression_list()

    async def _try_smtp_fallback(
        self,
        task: DomainTask,
        emails_found: Set[str],
        reason_code: str,
        details: str = "",
    ) -> Tuple[bool, List[Dict]]:
        """Try SMTP fallback when form submission fails.

        This method is called in various failure scenarios:
        - CAPTCHA detected
        - Form validation failed
        - Submit button not found
        - Form still present after submission
        - No form found

        Returns: (success, results)
        """
        results = []
        domain = task.domain

        click.echo(f"  📧 Intentando fallback por SMTP...")

        # Get target email
        target_email = task.target_email
        if not target_email and emails_found:
            target_email = emails_found.pop()  # Use first found email

        if target_email:
            if target_email.lower() in self.suppression_list:
                log_result(
                    domain,
                    "EMAIL",
                    "SKIPPED",
                    "SUPPRESSED",
                    f"Email {target_email} in suppression list (fallback for: {reason_code})",
                )
                results.append(
                    {
                        "domain": domain,
                        "action": "email",
                        "status": "suppressed",
                        "fallback_for": reason_code,
                    }
                )
                click.echo(f"  ⛔ Email {target_email} en lista de supresión")
            else:
                success, message = await self.smtp_sender.send_email(target_email)

                if success:
                    log_result(
                        domain,
                        "EMAIL",
                        "SUCCESS",
                        "EMAIL_SENT",
                        f"To: {target_email} (fallback for: {reason_code})",
                    )
                    results.append(
                        {
                            "domain": domain,
                            "action": "email",
                            "status": "success",
                            "fallback_for": reason_code,
                        }
                    )
                    click.echo(f"  ✅ Email enviado a {target_email} (fallback)")
                    stats.increment_message_sent(success=True)
                    return True, results
                else:
                    if "Hard bounce" in message:
                        add_to_suppression_list(target_email, f"Hard bounce from SMTP (fallback for: {reason_code})")
                        log_result(
                            domain,
                            "EMAIL",
                            "FAILED",
                            "HARD_BOUNCE",
                            f"To: {target_email}, Error: {message}",
                        )
                        results.append(
                            {
                                "domain": domain,
                                "action": "email",
                                "status": "hard_bounce",
                                "fallback_for": reason_code,
                            }
                        )
                        click.echo(f"  ❌ Hard bounce detectado para {target_email}")
                        stats.increment_message_sent(success=False)
                    else:
                        log_result(
                            domain,
                            "EMAIL",
                            "FAILED",
                            "SMTP_ERROR",
                            f"To: {target_email}, Error: {message}",
                        )
                        results.append(
                            {
                                "domain": domain,
                                "action": "email",
                                "status": "failed",
                                "error": message,
                                "fallback_for": reason_code,
                            }
                        )
                        click.echo(f"  ❌ Error SMTP: {message}")
                        stats.increment_message_sent(success=False)
        else:
            log_result(
                domain,
                "EMAIL",
                "FAILED",
                "NO_EMAIL_FOUND",
                f"No contact form or email found (fallback for: {reason_code})",
            )
            results.append(
                {
                    "domain": domain,
                    "action": "none",
                    "status": "no_contact_found",
                    "fallback_for": reason_code,
                }
            )
            click.echo(f"  ❌ No se encontró email de contacto para fallback")

        return False, results

    async def process_domain(self, task: DomainTask) -> List[Dict]:
        """Process a single domain."""
        results = []
        domain = task.domain

        # Check if domain is blacklisted
        if is_domain_blacklisted(domain):
            click.echo(f"⛏️ Dominio en blacklist omitido: {domain}")
            log_result(domain, "SKIP", "SKIPPED", "BLACKLISTED", "Domain in blacklist")
            results.append({"domain": domain, "action": "skip", "reason": "BLACKLISTED"})
            return results

        # Initialize logger for this domain
        evidence_logger.set_log_file(domain)

        log(f"\n{'='*60}")
        log(f"🌐 Procesando: {domain}")
        log(f"{'='*60}")

        # Crear directorio de evidencias si no existe
        evidence_dir = Path(EVIDENCE_DIR)
        evidence_dir.mkdir(exist_ok=True)
        log(f"  📁 Directorio de evidencias: {evidence_dir.absolute()}")
        log(f"  📝 Archivo de log: {evidence_logger.get_log_path()}")

        # Crawl the domain
        crawler = WebCrawler(task)
        forms, emails = await crawler.crawl()

        predefined_count = 4  # contacto, contacto/, contact, contact/
        # La homepage es seed, las predefinidas son las de contacto, el resto son dinámicas
        seed_count = 1  # homepage
        dynamic_count = max(0, len(task.visited_urls) - predefined_count - seed_count)

        # Update statistics
        valid_urls = len([url for url in task.visited_urls if url])
        invalid_urls = len(task.visited_urls) - valid_urls
        stats.add_urls_analyzed(len(task.visited_urls), valid=True)
        stats.add_urls_analyzed(0, valid=False)  # Contamos válidas por ahora
        stats.add_emails_found(emails, domain)

        log(f"\n  📊 Resultados del crawling:")
        log(f"     - Página inicial (seed): {seed_count}")
        log(f"     - Páginas predefinidas visitadas: {predefined_count}")
        log(f"     - Páginas dinámicas visitadas: {dynamic_count} (max: {MAX_PAGES_PER_DOMAIN})")
        log(f"     - Total páginas visitadas: {len(task.visited_urls)}")
        log(f"     - URLs visitadas:")
        for i, visited_url in enumerate(task.visited_urls, 1):
            url_type = "seed" if i == 1 else ("predefinida" if i <= 5 else "dinámica")
            log(f"       {i}. [{url_type}] {visited_url}")
        log(f"     - Formularios encontrados: {len(forms)}")
        log(f"     - Emails encontrados: {len(emails)} (total únicos: {len(stats.emails_extracted)})")

        # Delay de 3 minutos después de extracción antes de enviar
        log(f"\n  ⏱️  Pausa de 3 minutos antes de enviar...")
        await asyncio.sleep(180)  # 3 minutos = 180 segundos
        log(f"  ✅ Pausa completada, continuando con envíos...")

        # Process forms - solo 1 mensaje por dominio
        form_submitted = False
        skipped_forms = 0

        if forms:
            for form in forms:
                # CAPTCHA detected - try SMTP fallback instead of skipping
                if form.has_captcha:
                    code = f"HAS_{form.captcha_type.upper().replace(' ', '_')}"
                    click.echo(f"  ⚠️  {code} detectado en {form.url}")
                    click.echo(f"  📧 Intentando fallback por SMTP debido a CAPTCHA...")
                    success, fallback_results = await self._try_smtp_fallback(
                        task, emails, code, f"Form at {form.url}"
                    )
                    results.extend(fallback_results)
                    if success:
                        form_submitted = True
                        break
                    skipped_forms += 1
                    continue

                # Honeypot detected - try SMTP fallback instead of skipping
                if form.has_honeypot:
                    click.echo(f"  ⚠️  Honeypot detectado en {form.url}")
                    click.echo(f"  📧 Intentando fallback por SMTP debido a honeypot...")
                    success, fallback_results = await self._try_smtp_fallback(
                        task, emails, "HONEYPOT_DETECTED", f"Form at {form.url}"
                    )
                    results.extend(fallback_results)
                    if success:
                        form_submitted = True
                        break
                    skipped_forms += 1
                    continue

                # Submit the form
                click.echo(f"  📝 Intentando enviar formulario en {form.url}")
                success, message, evidence = await self.form_submitter.submit_form(form)

                if success:
                    log_result(domain, "FORM_SUBMIT", "SUCCESS", "FORM_SUBMITTED_SUCCESS", f"Form at {form.url}", evidence)
                    results.append({"domain": domain, "action": "form_submit", "status": "success"})
                    click.echo(f"  ✅ Formulario enviado exitosamente")
                    stats.increment_form_submitted(success=True)
                    stats.increment_message_sent(success=True)
                    form_submitted = True

                    # Informar cuántos formularios adicionales fueron ignorados
                    remaining_forms = len(forms) - skipped_forms - 1
                    if remaining_forms > 0:
                        click.echo(f"  ℹ️  {remaining_forms} formulario(s) adicional(es) ignorado(s) (límite: 1 por dominio)")
                    break  # Detener después del primer éxito (1 mensaje por dominio)
                else:
                    # Form submission failed - check if we should fallback to SMTP
                    log_result(domain, "FORM_SUBMIT", "FAILED", message, f"Form at {form.url}")
                    results.append({"domain": domain, "action": "form_submit", "status": "failed", "error": message})
                    click.echo(f"  ❌ Error al enviar formulario: {message}")
                    stats.increment_form_submitted(success=False)

                    # Try SMTP fallback for various error conditions
                    should_fallback = any(
                        error_code in message
                        for error_code in [
                            "FORM_FILL_ERROR",
                            "FORM_SUBMIT_ERROR",
                            "FORM_VALIDATION_FAILED",
                            "NO_SUCCESS_CONFIRMATION",
                        ]
                    )

                    if should_fallback:
                        click.echo(f"  📧 Intentando fallback por SMTP debido a error en formulario...")
                        fallback_success, fallback_results = await self._try_smtp_fallback(
                            task, emails, message, f"Form at {form.url}"
                        )
                        results.extend(fallback_results)
                        if fallback_success:
                            form_submitted = True
                            break

                    # Continuar con el siguiente formulario si hay más disponibles

        # Si no se envió ningún formulario (incluyendo NO_FORM_FOUND), intentar fallback por email
        if not form_submitted:
            log(f"  📧 No se pudo enviar formulario, intentando envío por email...")
            success, fallback_results = await self._try_smtp_fallback(
                task, emails, "NO_FORM_FOUND", "No contact form submitted successfully"
            )
            results.extend(fallback_results)

        # Cerrar archivo de log
        evidence_logger.close()

        return results

    async def process_all(self, tasks: List[DomainTask]) -> List[Dict]:
        """Process all domains with progress tracking."""
        all_results = []
        stats.set_total_domains(len(tasks))
        stats.start()

        click.echo(f"\n🚀 Iniciando procesamiento de {len(tasks)} dominios...")
        click.echo(f"{'='*70}")

        for task in tasks:
            try:
                results = await self.process_domain(task)
                all_results.extend(results)
                stats.increment_domain()

                # Show progress after each domain
                click.echo(stats.get_progress())

            except Exception as e:
                click.echo(f"  💥 Error crítico procesando {task.domain}: {e}")
                log_result(task.domain, "PROCESS", "ERROR", "UNKNOWN_ERROR", str(e))
                all_results.append({"domain": task.domain, "action": "error", "error": str(e)})
                stats.increment_domain()

        # Save extracted emails
        emails_file = stats.save_emails_to_file()
        click.echo(f"\n📧 Emails extraídos guardados en: {emails_file}")

        return all_results


# =============================================================================
# CLI
# =============================================================================

@click.group()
def cli():
    """Form Tester - Automated Contact Form Testing Tool."""
    pass


async def _run_pipeline(tasks: List[DomainTask]):
    """Run pipeline mode (1 crawler + 1 sender)."""
    from src.pipeline_runner import PipelineRunner
    from playwright.async_api import async_playwright

    runner = PipelineRunner()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        form_submitter = FormSubmitter(browser)
        smtp_sender = SMTPSender()

        results = await runner.run(
            tasks=tasks,
            stats=stats,
            evidence_logger=evidence_logger,
            form_submitter=form_submitter,
            smtp_sender=smtp_sender,
        )

        await browser.close()

    # Print summary
    click.echo(f"\n{'='*60}")
    click.echo(f"✅ Pipeline completado")
    click.echo(f"{'='*60}")
    click.echo(f"Crawler: {results['crawler']['processed']}/{results['crawler']['total']}")
    click.echo(f"Sender: {results['sender']['successful']}/{results['sender']['processed']} exitosos")

    return results


@cli.command()
@click.option("--schedule", "-s", help="Schedule execution for a future time (format: YYYY-MM-DD HH:MM)")
@click.option("--domain", "-d", help="Process a single domain instead of reading from domains.csv")
@click.option("--output", "-o", default=RESULTS_FILE, help="Output CSV file for results")
def process(schedule: Optional[str], domain: Optional[str], output: str):
    """Process all domains using pipeline mode (1 crawler + 1 sender with 3-min delay)."""

    # Handle scheduling
    if schedule:
        scheduled_time = datetime.strptime(schedule, "%Y-%m-%d %H:%M")
        now = datetime.now()

        if scheduled_time > now:
            wait_seconds = (scheduled_time - now).total_seconds()
            click.echo(f"⏰ Ejecución programada para {schedule}")
            click.echo(f"   Esperando {int(wait_seconds)} segundos...")
            time.sleep(wait_seconds)

    # Load domains
    if domain:
        tasks = [DomainTask(domain)]
    else:
        tasks = load_domains()

    if not tasks:
        click.echo("⚠️  No hay dominios para procesar")
        return

    click.echo(f"📋 Procesando {len(tasks)} dominio(s) en modo pipeline...")

    # Process domains using pipeline
    results = asyncio.run(_run_pipeline(tasks))

    # Summary
    click.echo(f"\n{'='*60}")
    click.echo(f"📊 RESUMEN")
    click.echo(f"{'='*60}")
    click.echo(f"   Total procesados: {len(tasks)}")
    click.echo(f"   Crawler: {results['crawler']['processed']}/{results['crawler']['total']}")
    click.echo(f"   Sender: {results['sender']['successful']}/{results['sender']['processed']} exitosos")
    click.echo(f"   Resultados guardados en: {output}")

    # Mostrar archivos de log generados
    evidence_dir = Path(EVIDENCE_DIR)
    if evidence_dir.exists():
        log_files = list(evidence_dir.glob("*.log"))
        click.echo(f"   Logs generados: {len(log_files)}")
        if len(log_files) > 0:
            click.echo(f"   📁 Ubicación: {evidence_dir.absolute()}")
    else:
        click.echo(f"   ⚠️  Directorio de evidencias no existe: {EVIDENCE_DIR}")


@cli.command()
def init():
    """Initialize the project with sample files and library."""
    create_sample_domains_file(DOMAINS_FILE)
    click.echo(f"✅ Archivo {DOMAINS_FILE} creado")
    click.echo(f"✅ Directorio {EVIDENCE_DIR}/ creado")
    Path(EVIDENCE_DIR).mkdir(exist_ok=True)

    # Create library files
    create_sample_smtp_accounts_file()
    create_sample_messages_file()
    create_sample_contacts_file()

    click.echo("\nPróximos pasos:")
    click.echo(f"  1. Edita {DOMAINS_FILE} y agrega los dominios a probar")
    click.echo(f"  2. Configura las variables de entorno SMTP (opcional si usas smtp_accounts.csv):")
    click.echo(f"     - FORM_TESTER_SMTP_USER")
    click.echo(f"     - FORM_TESTER_SMTP_PASSWORD")
    click.echo(f"     - FORM_TESTER_FROM_EMAIL")
    click.echo(f"  3. Personaliza smtp_accounts.csv para múltiples cuentas SMTP")
    click.echo(f"  4. Personaliza messages.csv para diferentes templates de mensajes")
    click.echo(f"  5. Personaliza contacts.csv para diferentes datos de contacto")
    click.echo(f"  6. Ejecuta: python main.py process")


@cli.command()
@click.argument("email")
def suppress(email: str):
    """Add an email to the suppression list."""
    add_to_suppression_list(email, "Manual addition")
    click.echo(f"✅ Email {email} agregado a la lista de supresión")


if __name__ == "__main__":
    cli()
