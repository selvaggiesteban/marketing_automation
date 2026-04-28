"""Sender worker - 1 único worker que procesa envíos con rate limit."""

import asyncio
from typing import List, Dict, Any
import click

from src.pipeline_queue import PipelineQueue, PipelineItem
from src.rate_limiter import RateLimiter


class SenderWorker:
    """Sender único que procesa cola con rate limiting.

    Espera 3 minutos entre cada envío.
    """

    def __init__(
        self,
        queue: PipelineQueue,
        rate_limiter: RateLimiter,
        form_submitter: Any,
        smtp_sender: Any,
    ):
        self.queue = queue
        self.rate_limiter = rate_limiter
        self.form_submitter = form_submitter
        self.smtp_sender = smtp_sender
        self._processed = 0
        self._successful = 0
        self._failed = 0

    async def process_item(
        self,
        item: PipelineItem,
        stats: Any,
        evidence_logger: Any,
    ) -> Dict:
        """Procesar un item de la cola."""
        from main import log_result, log, add_to_suppression_list, suppression_list

        domain = item.task.domain
        forms = item.forms or []
        emails = item.emails or set()
        results = []
        form_submitted = False
        skipped_forms = 0

        # Aplicar rate limit (esperar 3 min desde el último envío)
        wait_time = self.rate_limiter.get_time_until_next()
        if wait_time > 0:
            log(f"\n  ⏱️  Esperando {wait_time/60:.1f} min para rate limit...")
        await self.rate_limiter.acquire()

        log(f"\n  🚀 Iniciando envío para: {domain}")

        # Intentar formularios
        if forms:
            for form in forms:
                # CAPTCHA
                if form.has_captcha:
                    code = f"HAS_{form.captcha_type.upper().replace(' ', '_')}"
                    click.echo(f"  ⚠️  {code} detectado")
                    success, fallback_results = await self._try_smtp_fallback(
                        item, emails, code
                    )
                    results.extend(fallback_results)
                    if success:
                        form_submitted = True
                        break
                    skipped_forms += 1
                    continue

                # Honeypot
                if form.has_honeypot:
                    click.echo(f"  ⚠️  Honeypot detectado")
                    success, fallback_results = await self._try_smtp_fallback(
                        item, emails, "HONEYPOT_DETECTED"
                    )
                    results.extend(fallback_results)
                    if success:
                        form_submitted = True
                        break
                    skipped_forms += 1
                    continue

                # Enviar formulario
                click.echo(f"  📝 Enviando formulario...")
                success, message, evidence = await self.form_submitter.submit_form(form)

                if success:
                    log_result(domain, "FORM_SUBMIT", "SUCCESS", "FORM_SUBMITTED_SUCCESS", f"Form at {form.url}", evidence)
                    results.append({"domain": domain, "action": "form_submit", "status": "success"})
                    click.echo(f"  ✅ Formulario enviado")
                    stats.increment_form_submitted(success=True)
                    stats.increment_message_sent(success=True)
                    form_submitted = True
                    break
                else:
                    log_result(domain, "FORM_SUBMIT", "FAILED", message, f"Form at {form.url}")
                    results.append({"domain": domain, "action": "form_submit", "status": "failed", "error": message})
                    click.echo(f"  ❌ Error formulario: {message}")
                    stats.increment_form_submitted(success=False)

                    # Intentar SMTP fallback
                    if any(err in message for err in ["FORM_FILL_ERROR", "FORM_SUBMIT_ERROR", "FORM_VALIDATION_FAILED"]):
                        click.echo(f"  📧 Intentando SMTP fallback...")
                        success, fallback_results = await self._try_smtp_fallback(item, emails, message)
                        results.extend(fallback_results)
                        if success:
                            form_submitted = True
                            break

        # Si no se envió formulario, intentar SMTP
        if not form_submitted:
            log(f"  📧 Intentando envío por email...")
            success, fallback_results = await self._try_smtp_fallback(
                item, emails, "NO_FORM_FOUND"
            )
            results.extend(fallback_results)

        # Cerrar log
        evidence_logger.close()

        # Stats
        self._processed += 1
        if form_submitted or any(r.get("status") == "success" for r in results):
            self._successful += 1
        else:
            self._failed += 1

        return {
            "domain": domain,
            "success": form_submitted or any(r.get("status") == "success" for r in results),
            "results": results,
        }

    async def _try_smtp_fallback(
        self,
        item: PipelineItem,
        emails_found: set,
        reason_code: str,
    ) -> tuple[bool, List[Dict]]:
        """Intentar fallback por SMTP."""
        from main import log_result, click, add_to_suppression_list, suppression_list

        results = []
        domain = item.task.domain
        target_email = item.task.target_email

        if not target_email and emails_found:
            target_email = emails_found.pop() if emails_found else None

        if not target_email:
            log_result(domain, "EMAIL", "FAILED", "NO_EMAIL_FOUND", f"No contact found")
            results.append({"domain": domain, "action": "none", "status": "no_contact_found"})
            click.echo(f"  ❌ No hay email para fallback")
            return False, results

        if target_email.lower() in suppression_list:
            log_result(domain, "EMAIL", "SKIPPED", "SUPPRESSED", f"Email {target_email} suppressed")
            results.append({"domain": domain, "action": "email", "status": "suppressed"})
            click.echo(f"  ⛔ Email en lista de supresión")
            return False, results

        # Enviar email
        success, message = await self.smtp_sender.send_email(target_email)

        if success:
            log_result(domain, "EMAIL", "SUCCESS", "EMAIL_SENT", f"To: {target_email}")
            results.append({"domain": domain, "action": "email", "status": "success"})
            click.echo(f"  ✅ Email enviado a {target_email}")
            return True, results
        else:
            if "Hard bounce" in message:
                add_to_suppression_list(target_email, f"Hard bounce: {message}")
                log_result(domain, "EMAIL", "FAILED", "HARD_BOUNCE", message)
                results.append({"domain": domain, "action": "email", "status": "hard_bounce"})
            else:
                log_result(domain, "EMAIL", "FAILED", "SMTP_ERROR", message)
                results.append({"domain": domain, "action": "email", "status": "failed", "error": message})
            click.echo(f"  ❌ Error SMTP: {message}")
            return False, results

    async def run(
        self,
        stats: Any,
        evidence_logger: Any,
    ) -> dict:
        """Procesar cola hasta que esté vacía y completada."""
        click.echo(f"\n📤 Sender iniciado - esperando items...")
        click.echo(f"   Rate limit: 3 minutos entre envíos")
        click.echo(f"{'='*70}")

        while not self.queue.all_done():
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            if item.error:
                click.echo(f"  ⚠️  Item con error, saltando: {item.task.domain}")
                self.queue.task_done()
                self._failed += 1
                continue

            try:
                result = await self.process_item(item, stats, evidence_logger)
                self.queue.task_done()

                # Mostrar progreso
                click.echo(stats.get_progress())

            except Exception as e:
                click.echo(f"  💥 Error procesando {item.task.domain}: {e}")
                self.queue.task_done()
                self._failed += 1

        click.echo(f"\n✅ Sender completado:")
        click.echo(f"   Procesados: {self._processed}")
        click.echo(f"   Exitosos: {self._successful}")
        click.echo(f"   Fallidos: {self._failed}")

        return {
            "processed": self._processed,
            "successful": self._successful,
            "failed": self._failed,
        }

    def get_stats(self) -> dict:
        return {
            "processed": self._processed,
            "successful": self._successful,
            "failed": self._failed,
        }
