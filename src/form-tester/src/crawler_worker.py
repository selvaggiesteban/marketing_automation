"""Crawler worker - 1 único worker que procesa dominios secuencialmente."""

from typing import List, Any
import click

from src.pipeline_queue import PipelineQueue, PipelineItem


class CrawlerWorker:
    """Crawler único que procesa dominios y encola resultados.

    Procesa dominios uno por uno (secuencial), pero el envío
    es independiente gracias a la cola.
    """

    def __init__(self, queue: PipelineQueue):
        self.queue = queue
        self._processed = 0
        self._failed = 0

    async def crawl_domain(
        self,
        task: Any,  # DomainTask
        stats: Any,  # Statistics
        evidence_logger: Any,
    ) -> bool:
        """Crawl un dominio y encolar resultado."""
        domain = task.domain

        try:
            # Importar de main (circular import)
            from main import (
                WebCrawler, is_domain_blacklisted, log, log_result,
                EVIDENCE_DIR, Path, MAX_PAGES_PER_DOMAIN
            )

            # Check blacklist
            if is_domain_blacklisted(domain):
                click.echo(f"⛏️ Dominio en blacklist omitido: {domain}")
                log_result(domain, "SKIP", "SKIPPED", "BLACKLISTED", "Domain in blacklist")
                self._failed += 1
                return False

            # Inicializar logger
            evidence_logger.set_log_file(domain)

            log(f"\n{'='*60}")
            log(f"🌐 Crawleando: {domain}")
            log(f"{'='*60}")

            # Crear directorio de evidencias
            evidence_dir = Path(EVIDENCE_DIR)
            evidence_dir.mkdir(exist_ok=True)

            # Crawl
            crawler = WebCrawler(task)
            forms, emails = await crawler.crawl()

            # Actualizar stats
            stats.add_urls_analyzed(len(task.visited_urls), valid=True)
            stats.add_emails_found(emails, domain)

            log(f"\n  📊 Crawling completado:")
            log(f"     - URLs visitadas: {len(task.visited_urls)}")
            log(f"     - Formularios: {len(forms)}")
            log(f"     - Emails: {len(emails)} (total únicos: {len(stats.emails_extracted)})")

            # Encolar para envío
            queue_item = PipelineItem(
                task=task,
                forms=forms,
                emails=emails,
                crawl_results={
                    "urls_visited": len(task.visited_urls),
                    "forms_found": len(forms),
                    "emails_found": len(emails),
                }
            )
            await self.queue.put(queue_item)

            log(f"  ✅ Encolado para envío: {domain}")
            self._processed += 1
            return True

        except Exception as e:
            click.echo(f"  💥 Error crawl {domain}: {e}")
            log_result(domain, "CRAWL", "ERROR", "CRAWL_FAILED", str(e))
            self._failed += 1

            # Encolar como failed
            await self.queue.put(PipelineItem(
                task=task,
                error=str(e)
            ))
            return False

    async def run(
        self,
        tasks: List[Any],
        stats: Any,
        evidence_logger: Any,
    ) -> dict:
        """Procesar todos los dominios secuencialmente."""
        click.echo(f"\n🕷️  Crawler iniciado - {len(tasks)} dominios")
        click.echo(f"{'='*70}")

        for task in tasks:
            await self.crawl_domain(task, stats, evidence_logger)

        click.echo(f"\n✅ Crawling completado: {self._processed}/{len(tasks)}")
        return {
            "processed": self._processed,
            "failed": self._failed,
            "total": len(tasks),
        }

    def get_stats(self) -> dict:
        return {
            "processed": self._processed,
            "failed": self._failed,
        }
