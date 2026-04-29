"""Pipeline runner - ejecuta crawler y sender concurrentemente."""

import asyncio
from typing import List, Any
import click

from src.pipeline_queue import PipelineQueue
from src.rate_limiter import RateLimiter
from src.crawler_worker import CrawlerWorker
from src.sender_worker import SenderWorker


class PipelineRunner:
    """Ejecuta el pipeline completo: 1 crawler + 1 sender.

    El crawler y sender corren concurrentemente:
    - Crawler encola resultados a medida que los obtiene
    - Sender espera en la cola y procesa con rate limit
    """

    def __init__(self):
        self.queue = None
        self.rate_limiter = None
        self.crawler = None
        self.sender = None

    async def run(
        self,
        tasks: List[Any],
        stats: Any,
        evidence_logger: Any,
        form_submitter: Any,
        smtp_sender: Any,
    ) -> dict:
        """Ejecutar pipeline completo."""

        click.echo(f"\n{'='*70}")
        click.echo(f"🚀 Modo: Pipeline (1 Crawler + 1 Sender)")
        click.echo(f"   Dominios: {len(tasks)}")
        click.echo(f"   Delay entre envíos: 3 minutos")
        click.echo(f"{'='*70}\n")

        # Inicializar
        stats.set_total_domains(len(tasks))
        stats.start()

        self.queue = PipelineQueue(total_items=len(tasks))
        self.rate_limiter = RateLimiter(min_delay_seconds=180.0)  # 3 min

        self.crawler = CrawlerWorker(queue=self.queue)
        self.sender = SenderWorker(
            queue=self.queue,
            rate_limiter=self.rate_limiter,
            form_submitter=form_submitter,
            smtp_sender=smtp_sender,
        )

        # Ejecutar ambos concurrentemente
        try:
            # Usar gather para correr ambos "al mismo tiempo"
            # El sender empieza a procesar tan pronto hay items en cola
            crawler_task = asyncio.create_task(
                self.crawler.run(tasks, stats, evidence_logger)
            )
            sender_task = asyncio.create_task(
                self.sender.run(stats, evidence_logger)
            )

            # Esperar a que ambos terminen
            crawler_results, sender_results = await asyncio.gather(
                crawler_task, sender_task
            )

            # Guardar emails extraídos
            from main import stats as main_stats
            emails_file = main_stats.save_emails_to_file()
            click.echo(f"\n📧 Emails guardados en: {emails_file}")

            return {
                "crawler": crawler_results,
                "sender": sender_results,
            }

        except Exception as e:
            click.echo(f"\n💥 Error en pipeline: {e}")
            raise

    def get_stats(self) -> dict:
        """Estadísticas del pipeline."""
        return {
            "queue": self.queue.get_stats() if self.queue else {},
            "crawler": self.crawler.get_stats() if self.crawler else {},
            "sender": self.sender.get_stats() if self.sender else {},
        }
