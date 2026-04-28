"""Rate limiter para delay entre envíos."""

import asyncio
from datetime import datetime, timedelta
from typing import Optional


class RateLimiter:
    """Rate limiter con delay global de 3 minutos."""

    def __init__(self, min_delay_seconds: float = 180.0):  # 3 minutes
        self.min_delay = timedelta(seconds=min_delay_seconds)
        self.last_send_time: Optional[datetime] = None
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Adquirir permiso, esperando si es necesario."""
        async with self._lock:
            if self.last_send_time is not None:
                elapsed = datetime.now() - self.last_send_time
                if elapsed < self.min_delay:
                    wait_seconds = (self.min_delay - elapsed).total_seconds()
                    await asyncio.sleep(wait_seconds)
            self.last_send_time = datetime.now()

    def get_time_until_next(self) -> float:
        """Segundos hasta el próximo envío permitido."""
        if self.last_send_time is None:
            return 0.0
        elapsed = datetime.now() - self.last_send_time
        remaining = self.min_delay - elapsed
        return max(0.0, remaining.total_seconds())
