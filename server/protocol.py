import json
from typing import Dict, Any


def encode_message(message: Dict[str, Any]) -> str:
    """Encode a message dictionary to JSON string."""
    return json.dumps(message)


def decode_message(data: str) -> Dict[str, Any]:
    """Decode a JSON string to message dictionary."""
    return json.loads(data)


def create_input_message(player_id: str, move: str) -> Dict[str, Any]:
    """Create a client input message."""
    return {
        "type": "input",
        "id": player_id,
        "move": move
    }


def create_state_message(game_state) -> Dict[str, Any]:
    """Create a state broadcast message from game state."""
    return game_state.to_dict()


def create_welcome_message(player_id: str) -> Dict[str, Any]:
    """Create a welcome message for new players."""
    return {
        "type": "welcome",
        "player_id": player_id,
        "message": "Connected to game server"
    }


def create_error_message(error: str) -> Dict[str, Any]:
    """Create an error message."""
    return {
        "type": "error",
        "message": error
    }