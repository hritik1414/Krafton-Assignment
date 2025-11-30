import asyncio
import websockets
from typing import Set
from websockets.server import WebSocketServerProtocol


class NetworkManager:
    """Manages WebSocket connections and network communication."""
    
    def __init__(self, artificial_latency: float = 0.2):
        self.clients: Set[WebSocketServerProtocol] = set()
        self.artificial_latency = artificial_latency
    
    def register_client(self, websocket: WebSocketServerProtocol) -> None:
        """Register a new client connection."""
        self.clients.add(websocket)
    
    def unregister_client(self, websocket: WebSocketServerProtocol) -> None:
        """Unregister a client connection."""
        self.clients.discard(websocket)
    
    async def send_message(self, websocket: WebSocketServerProtocol, message: str) -> None:
        """Send a message to a specific client with artificial latency."""
        try:
            # Simulate network latency
            await asyncio.sleep(self.artificial_latency)
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            pass
    
    async def broadcast_message(self, message: str) -> None:
        """Broadcast a message to all connected clients with artificial latency."""
        if self.clients:
            # Simulate network latency before broadcasting
            await asyncio.sleep(self.artificial_latency)
            
            # Send to all clients
            tasks = []
            for websocket in self.clients.copy():
                tasks.append(self._send_without_latency(websocket, message))
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_without_latency(self, websocket: WebSocketServerProtocol, message: str) -> None:
        """Internal method to send without additional latency."""
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            self.unregister_client(websocket)
    
    async def receive_message(self, websocket: WebSocketServerProtocol) -> str:
        """Receive a message from a client with artificial latency."""
        message = await websocket.recv()
        # Simulate network latency on receive
        await asyncio.sleep(self.artificial_latency)
        return message