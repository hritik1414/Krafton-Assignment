import asyncio
import websockets
import pygame
import json
import sys
from client.renderer import Renderer
from client.input_handler import InputHandler
from client.interpolation import StateBuffer


class GameClient:
    """Main game client that connects to server and runs the game."""
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.renderer = Renderer()
        self.input_handler = InputHandler()
        self.state_buffer = StateBuffer(max_size=30, interpolation_delay=0.1)
        
        self.websocket = None
        self.player_id = None
        self.running = True
        self.clock = pygame.time.Clock()
    
    async def connect(self):
        """Connect to the game server."""
        try:
            self.websocket = await websockets.connect(self.server_url)
            print(f"Connected to server at {self.server_url}")
            
            # Receive welcome message
            welcome_msg = await self.websocket.recv()
            welcome_data = json.loads(welcome_msg)
            
            if welcome_data.get("type") == "welcome":
                self.player_id = welcome_data.get("player_id")
                print(f"Assigned player ID: {self.player_id}")
        
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.running = False
    
    async def send_input(self, move: str):
        """Send input to server."""
        if self.websocket:
            try:
                message = {
                    "type": "input",
                    "id": self.player_id,
                    "move": move
                }
                await self.websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                print("Connection to server lost")
                self.running = False
    
    async def receive_updates(self):
        """Continuously receive state updates from server."""
        try:
            while self.running:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                if data.get("type") == "state":
                    # Add state to buffer for interpolation
                    timestamp = data.get("timestamp")
                    self.state_buffer.add_snapshot(timestamp, data)
        
        except websockets.exceptions.ConnectionClosed:
            print("Server connection closed")
            self.running = False
        except Exception as e:
            print(f"Error receiving updates: {e}")
            self.running = False
    
    async def game_loop(self):
        """Main game loop handling input and rendering."""
        receive_task = asyncio.create_task(self.receive_updates())
        
        try:
            while self.running:
                # Handle Pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                            break
                
                # Process input
                move = self.input_handler.process_input()
                if move is not None:
                    await self.send_input(move)
                
                # Get interpolated state and render
                interpolated_state = self.state_buffer.get_interpolated_state()
                self.renderer.render(interpolated_state, self.player_id)
                
                # Cap frame rate at 60 FPS
                self.clock.tick(60)
                
                # Small async yield to allow other tasks to run
                await asyncio.sleep(0)
        
        finally:
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
    
    async def run(self):
        """Run the game client."""
        await self.connect()
        
        if self.running:
            await self.game_loop()
        
        # Cleanup
        if self.websocket:
            await self.websocket.close()
        
        self.renderer.close()
        print("Client shut down")


async def main():
    """Entry point for the client."""
    server_url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8765"
    
    client = GameClient(server_url)
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient terminated by user")