from dataclasses import dataclass, field
from typing import List, Dict
import time


@dataclass
class PlayerState:
    """Represents a player's state in the game."""
    id: str
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    score: int = 0
    color: tuple = (255, 100, 100)
    radius: float = 20.0
    speed: float = 200.0  # pixels per second


@dataclass
class Coin:
    """Represents a collectible coin."""
    id: str
    x: float
    y: float
    value: int = 1
    radius: float = 10.0


@dataclass
class GameState:
    """Represents the entire game state."""
    players: Dict[str, PlayerState] = field(default_factory=dict)
    coins: List[Coin] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    world_width: float = 800.0
    world_height: float = 600.0
    
    def to_dict(self) -> dict:
        """Serialize game state to dictionary."""
        return {
            "type": "state",
            "timestamp": self.timestamp,
            "players": [
                {
                    "id": p.id,
                    "x": p.x,
                    "y": p.y,
                    "vx": p.vx,
                    "vy": p.vy,
                    "score": p.score,
                    "color": p.color,
                    "radius": p.radius
                }
                for p in self.players.values()
            ],
            "coins": [
                {
                    "id": c.id,
                    "x": c.x,
                    "y": c.y,
                    "value": c.value,
                    "radius": c.radius
                }
                for c in self.coins
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GameState':
        """Deserialize game state from dictionary."""
        state = cls()
        state.timestamp = data.get("timestamp", time.time())
        
        for p_data in data.get("players", []):
            player = PlayerState(
                id=p_data["id"],
                x=p_data["x"],
                y=p_data["y"],
                vx=p_data.get("vx", 0.0),
                vy=p_data.get("vy", 0.0),
                score=p_data.get("score", 0),
                color=tuple(p_data.get("color", [255, 100, 100])),
                radius=p_data.get("radius", 20.0)
            )
            state.players[player.id] = player
        
        for c_data in data.get("coins", []):
            coin = Coin(
                id=c_data["id"],
                x=c_data["x"],
                y=c_data["y"],
                value=c_data.get("value", 1),
                radius=c_data.get("radius", 10.0)
            )
            state.coins.append(coin)
        
        return state