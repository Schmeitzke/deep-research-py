import asyncio
import time

class RateLimiter:
    def __init__(self, interval: float):
        self.interval = interval
        self.lock = asyncio.Lock()
        self.last_called = 0.0

    async def wait(self):
        async with self.lock:
            now = time.monotonic()
            wait_time = self.interval - (now - self.last_called)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_called = time.monotonic()

global_rate_limiter = RateLimiter(2)
