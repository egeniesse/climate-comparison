import asyncio
import collections
import logging
import time
import uuid

logger = logging.getLogger(__name__)

class ThrottledHttpClient:
    def __init__(self, session, cooldown, headers=None):
        self.session = session
        self.headers = headers or {}
        self.cooldown = cooldown
        self.cooldown_expires = time.time()
        self.request_queue = collections.deque()
    
    async def get(self, url, **kwargs):
        await self._wait_for_turn()
        retry_count = 0
        while retry_count < 15:
            try:
                return await self.session.get(url, raise_for_status=True, **kwargs)
            except Exception as e:
                logger.warn(f"Failed to fetch data due to: {e}")
                retry_count += 1
                await asyncio.sleep(retry_count ** 3)
    
    async def _wait_for_turn(self):
        request_id = str(uuid.uuid4())
        self.request_queue.append(request_id)
        while self.request_queue[0] != request_id or time.time() < self.cooldown_expires:
            await asyncio.sleep(0.5)
        self.cooldown_expires = time.time() + self.cooldown
        self.request_queue.popleft()
