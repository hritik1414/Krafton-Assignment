# Krafton - Multiplayer Game

A real-time multiplayer game built with Python, featuring WebSocket-based client-server architecture, Pygame rendering, and network synchronization with interpolation.

## Project Overview

Krafton is a networked game where multiple players connect to a central server, control characters in a shared world, and compete to collect coins. The game demonstrates modern game development practices including:

- **Asynchronous networking** with WebSockets for real-time communication
- **Client-side interpolation** for smooth movement prediction
- **Server-side game logic** for authoritative game state management
- **Configurable parameters** via environment variables

## Project Structure

```
.
├── client/                    # Client-side game application
│   ├── __init__.py
│   ├── main.py               # Main game client and connection handler
│   ├── input_handler.py       # User input processing
│   ├── renderer.py            # Pygame rendering engine
│   ├── interpolation.py       # Client-side state interpolation
│   └── __pycache__/
├── server/                    # Server-side game engine
│   ├── __init__.py
│   ├── main.py                # Server entry point and game loop
│   ├── game_state.py          # Game world state management
│   ├── game_logic.py          # Core game mechanics
│   ├── network.py             # Network communication utilities
│   ├── protocol.py            # Message encoding/decoding
│   └── __pycache__/
├── tests/                     # Unit tests
│   ├── __init__.py
│   ├── test_game_logic.py     # Game logic tests
│   └── test_interpolation.py  # Interpolation tests
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Dependencies

- **websockets** (12.0) - WebSocket protocol implementation for real-time networking
- **pygame** (2.5.2) - Game rendering and window management
- **pytest** (7.4.3) - Testing framework
- **black** (23.12.1) - Code formatting
- **ruff** (0.1.8) - Fast Python linter
- **mypy** (1.7.1) - Static type checking
- **python-dotenv** (1.0.0) - Environment variable management

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The project uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

```env
# Server Configuration
SERVER_HOST=localhost
SERVER_PORT=8765
TICK_RATE=30
COIN_SPAWN_INTERVAL=3.0
ARTIFICIAL_LATENCY=0.2
WORLD_WIDTH=800
WORLD_HEIGHT=600

# Client Configuration
SERVER_URL=ws://localhost:8765
```

## Running the Game

### Start the Server

```bash
python -m server.main
```

The server will start listening on the configured host and port (default: `localhost:8765`).

### Start the Client

```bash
python -m client.main
```

The client will connect to the server and launch the Pygame window.

### Multiple Players

Run multiple instances of the client to connect different players to the same server:

```bash
# Terminal 1: Start server
python -m server.main

# Terminal 2: Start player 1
python -m client.main

# Terminal 3: Start player 2
python -m client.main

# Add more as needed...
```

## Running Tests

Execute the test suite with pytest:

```bash
pytest tests/
```

For coverage information:
```bash
pytest tests/ --cov
```

## Code Quality

The project uses several tools for code quality:

- **Format code**: `black .`
- **Lint code**: `ruff check .`
- **Type check**: `mypy .`

## Architecture Overview

### Server Architecture

The server maintains the authoritative game state and handles:
- Player connection/disconnection
- Game logic updates (movement, collisions, scoring)
- Coin spawning and collection
- Broadcasting state to all connected clients

**Key Components:**
- `GameState`: Stores the world state (players, coins, scores)
- `GameLogic`: Implements game mechanics (movement, collision detection)
- `NetworkManager`: Handles WebSocket communication and artificial latency
- `Protocol`: Encodes/decodes messages between client and server

### Client Architecture

The client renders the game and sends user input:
- Receives game state from server
- Interpolates between states for smooth motion
- Captures keyboard input
- Renders game world with Pygame

**Key Components:**
- `GameClient`: Main client loop and server connection
- `Renderer`: Pygame rendering engine
- `InputHandler`: Keyboard input processing
- `StateBuffer`: Client-side interpolation of player positions

## Game Mechanics

- **Players**: Connect to the server and control a character in the world
- **Movement**: Players move within the world boundaries
- **Coins**: Spawn at regular intervals; collecting coins increases score
- **Synchronization**: Client-side interpolation ensures smooth rendering despite network latency

## Networking Protocol

Messages are JSON-encoded with the following types:

- **welcome**: Server assigns a player ID upon connection
- **input**: Client sends movement commands
- **state**: Server broadcasts current game state to all clients

## Development

### Adding Features

1. Add game logic to `server/game_logic.py`
2. Update `server/game_state.py` to store new state
3. Modify protocol messages in `server/protocol.py`
4. Update client rendering in `client/renderer.py`
5. Add corresponding tests in `tests/`

### Debugging

Enable verbose logging by checking server console output and client connection messages. Use environment variables to adjust:
- `ARTIFICIAL_LATENCY`: Simulate network delay (useful for testing interpolation)
- `TICK_RATE`: Game loop update frequency

## Performance Considerations

- **Tick Rate**: Higher tick rates increase server CPU usage but improve responsiveness
- **Interpolation Delay**: Larger delays provide smoother motion but add input latency
- **Artificial Latency**: Useful for testing network robustness; disable in production


## Support

For issues or questions, please refer to the project documentation or contact the development team.
