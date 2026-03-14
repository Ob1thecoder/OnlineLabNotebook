"""
WebSocket consumer for real-time co-editing and presence.
Implemented in Phase 6 — Real-Time Collaboration.
"""
from channels.generic.websocket import AsyncWebsocketConsumer


class CollaborationConsumer(AsyncWebsocketConsumer):
    """Stub consumer — full implementation in Phase 6."""

    async def connect(self) -> None:
        await self.accept()

    async def disconnect(self, code: int) -> None:
        pass

    async def receive(self, text_data: str = "", bytes_data: bytes = b"") -> None:
        pass
