from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.request_connections: dict[int, list[WebSocket]] = defaultdict(list)
        self.provider_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect_request(self, request_id: int, websocket: WebSocket):
        await websocket.accept()
        self.request_connections[request_id].append(websocket)

    async def connect_provider(self, provider_id: int, websocket: WebSocket):
        await websocket.accept()
        self.provider_connections[provider_id].append(websocket)

    def disconnect_request(self, request_id: int, websocket: WebSocket):
        self._disconnect(self.request_connections, request_id, websocket)

    def disconnect_provider(self, provider_id: int, websocket: WebSocket):
        self._disconnect(self.provider_connections, provider_id, websocket)

    async def broadcast_request(self, request_id: int, payload: dict[str, Any]):
        await self._broadcast(self.request_connections, request_id, payload)

    async def broadcast_provider(self, provider_id: int, payload: dict[str, Any]):
        await self._broadcast(self.provider_connections, provider_id, payload)

    def _disconnect(self, bucket: dict[int, list[WebSocket]], key: int, websocket: WebSocket):
        if websocket in bucket.get(key, []):
            bucket[key].remove(websocket)
        if key in bucket and not bucket[key]:
            bucket.pop(key)

    async def _broadcast(self, bucket: dict[int, list[WebSocket]], key: int, payload: dict[str, Any]):
        stale_connections = []
        for websocket in bucket.get(key, []):
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self._disconnect(bucket, key, websocket)


manager = ConnectionManager()
