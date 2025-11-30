import asyncio
import websockets
import time
import os
from dotenv import load_dotenv
from server.game_state import GameState
from server.game_logic import (
    update_player_positions,
    set_player_velocity,
    resolve_coin_collisions,
    spawn_coin,
    add_player,
    remove_player
)
from server.protocol import (
    encode_message,
    decode_message,
    create_state_message,
    create_welcome_message
)
from server.network import NetworkManager

# Load environment variables
load_dotenv()

# Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8765"))
TICK_RATE = int(os.getenv("TICK_RATE", "30"))
COIN_SPAWN_INTERVAL = float(os.getenv("COIN_SPAWN_INTERVAL", "3.0"))
ARTIFICIAL_LATENCY = float(os.getenv("ARTIFICIAL_LATENCY", "0.2"))
WORLD_WIDTH = float(os.getenv("WORLD_WIDTH", "800"))
WORLD_HEIGHT = float(os.getenv("WORLD_HEIGHT", "600"))

# Global game state
game_state = GameState(world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT)
network_manager = NetworkManager(artificial_latency=ARTIFICIAL_LATENCY)

# Player ID to WebSocket mapping
player_connections = {}


async def handle_client_message(websocket, player_id: str):
    """Handle incoming messages from a client."""
    try:
        while True:
            message_str = await network_manager.receive_message(websocket)
            message = decode_message(message_str)
            
            # Only process input messages
            if message.get("type") == "input":
                move = message.get("move")
                if player_id in game_state.players:
                    set_player_velocity(game_state.players[player_id], move)
                    
    except websockets.exceptions.ConnectionClosed:
        pass


async def handle_client(websocket, path):
    """Handle a new client connection."""
    player_id = f"player_{id(websocket)}"
    
    # Register client
    network_manager.register_client(websocket)
    player_connections[player_id] = websocket
    
    # Add player to game
    add_player(game_state, player_id)
    
    # Send welcome message
    welcome_msg = create_welcome_message(player_id)
    await network_manager.send_message(websocket, encode_message(welcome_msg))
    
    print(f"Player {player_id} connected")
    
    try:
        # Handle client messages
        await handle_client_message(websocket, player_id)
    finally:
        # Cleanup on disconnect
        network_manager.unregister_client(websocket)
        remove_player(game_state, player_id)
        if player_id in player_connections:
            del player_connections[player_id]
        print(f"Player {player_id} disconnected")


async def game_loop():
    """Main game loop that updates game state and broadcasts to clients."""
    last_time = time.time()
    last_coin_spawn = time.time()
    
    while True:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Update game state
        update_player_positions(game_state, delta_time)
        resolve_coin_collisions(game_state)
        
        # Spawn coins periodically
        if current_time - last_coin_spawn >= COIN_SPAWN_INTERVAL:
            spawn_coin(game_state)
            last_coin_spawn = current_time
        
        # Update timestamp
        game_state.timestamp = current_time
        
        # Broadcast state to all clients
        state_message = create_state_message(game_state)
        await network_manager.broadcast_message(encode_message(state_message))
        
        # Sleep to maintain tick rate
        await asyncio.sleep(1.0 / TICK_RATE)


async def main():
    """Start the game server."""
    # Spawn a few initial coins
    for _ in range(5):
        spawn_coin(game_state)
    
    # Start game loop
    game_task = asyncio.create_task(game_loop())
    
    # Start WebSocket server
    print(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")
    async with websockets.serve(handle_client, SERVER_HOST, SERVER_PORT):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())