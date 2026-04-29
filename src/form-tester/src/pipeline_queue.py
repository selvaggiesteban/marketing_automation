"""Simple queue for pipeline coordination (1 crawler + 1 sender)."""

import asyncio
from dataclasses import dataclass
from typing import Optional, Set, List, Any


@dataclass
class PipelineItem:
    """Item en la cola con resultados del crawling."""
    task: Any  # DomainTask
    forms: Optional[List[Any]] = None
    emails: Optional[Set[str]] = None
    crawl_results: Optional[dict] = None
    error: Optional[str] = None


class PipelineQueue:
    """Cola simple entre crawler y sender.

    Unbounded queue - no hay límite de tamaño.
    """

    def __init__(self, total_items: Optional[int] = None):
        self._queue: asyncio.Queue[PipelineItem] = asyncio.Queue()
        self._completed = 0
        self._total = total_items

    async def put(self, item: PipelineItem) -> None:
        """Agregar item a la cola."""
        await self._queue.put(item)

    async def get(self) -> PipelineItem:
        """Obtener item de la cola (bloquea si vacía)."""
        return await self._queue.get()

    def task_done(self) -> None:
        """Marcar tarea como completada."""
        self._queue.task_done()
        self._completed += 1

    def qsize(self) -> int:
        """Items pendientes en cola."""
        return self._queue.qsize()

    def empty(self) -> bool:
        """Cola vacía."""
        return self._queue.empty()

    def all_done(self) -> bool:
        """Todas las tareas procesadas."""
        if self._total is None:
            return self.empty()
        return self._completed >= self._total

    def get_stats(self) -> dict:
        """Estadísticas de la cola."""
        return {
            "pending": self.qsize(),
            "completed": self._completed,
            "total": self._total,
        }
