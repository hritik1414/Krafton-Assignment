import random
import uuid
import math
from typing import List, Tuple
from server.game_state import GameState, PlayerState, Coin


def update_player_positions(game_state: GameState, delta_time: float) -> None:
    """Update all player positions based on their velocities."""
    for player in game_state.players.values():
        # Update position
        player.x += player.vx * delta_time
        player.y += player.vy * delta_time
        
        # Clamp to world boundaries
        player.x = max(player.radius, min(game_state.world_width - player.radius, player.x))
        player.y = max(player.radius, min(game_state.world_height - player.radius, player.y))


def set_player_velocity(player: PlayerState, direction: str) -> None:
    """Set player velocity based on input direction."""
    speed = player.speed
    
    if direction == "up":
        player.vx, player.vy = 0, -speed
    elif direction == "down":
        player.vx, player.vy = 0, speed
    elif direction == "left":
        player.vx, player.vy = -speed, 0
    elif direction == "right":
        player.vx, player.vy = speed, 0
    elif direction == "stop":
        player.vx, player.vy = 0, 0


def check_collision(x1: float, y1: float, r1: float, x2: float, y2: float, r2: float) -> bool:
    """Check if two circular objects collide."""
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance < (r1 + r2)


def resolve_coin_collisions(game_state: GameState) -> List[Tuple[str, str]]:
    """
    Check for player-coin collisions and remove collected coins.
    Returns list of (player_id, coin_id) tuples for collected coins.
    """
    collected = []
    coins_to_remove = []
    
    for coin in game_state.coins:
        for player in game_state.players.values():
            if check_collision(player.x, player.y, player.radius, coin.x, coin.y, coin.radius):
                player.score += coin.value
                coins_to_remove.append(coin)
                collected.append((player.id, coin.id))
                break
    
    # Remove collected coins
    for coin in coins_to_remove:
        game_state.coins.remove(coin)
    
    return collected


def spawn_coin(game_state: GameState) -> Coin:
    """Spawn a new coin at a random position."""
    coin = Coin(
        id=str(uuid.uuid4()),
        x=random.uniform(50, game_state.world_width - 50),
        y=random.uniform(50, game_state.world_height - 50),
        value=random.choice([1, 1, 1, 2, 5])  # Weighted towards 1 point coins
    )
    game_state.coins.append(coin)
    return coin


def add_player(game_state: GameState, player_id: str) -> PlayerState:
    """Add a new player to the game at a random spawn position."""
    colors = [
        (255, 100, 100),  # Red
        (100, 255, 100),  # Green
        (100, 100, 255),  # Blue
        (255, 255, 100),  # Yellow
        (255, 100, 255),  # Magenta
        (100, 255, 255),  # Cyan
    ]
    
    player = PlayerState(
        id=player_id,
        x=random.uniform(100, game_state.world_width - 100),
        y=random.uniform(100, game_state.world_height - 100),
        color=random.choice(colors)
    )
    game_state.players[player_id] = player
    return player


def remove_player(game_state: GameState, player_id: str) -> None:
    """Remove a player from the game."""
    if player_id in game_state.players:
        del game_state.players[player_id]