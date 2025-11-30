import time
from typing import List, Tuple, Optional, Dict
from collections import deque


class StateBuffer:
    """Buffer for storing game state snapshots for interpolation."""
    
    def __init__(self, max_size: int = 30, interpolation_delay: float = 0.1):
        self.buffer: deque = deque(maxlen=max_size)
        self.interpolation_delay = interpolation_delay
    
    def add_snapshot(self, timestamp: float, state: dict) -> None:
        """Add a new state snapshot to the buffer."""
        self.buffer.append((timestamp, state))
    
    def get_interpolated_state(self) -> Optional[dict]:
        """
        Get an interpolated state based on current time minus interpolation delay.
        Returns None if not enough snapshots are available.
        """
        if len(self.buffer) < 2:
            return None
        
        # Calculate render time (current time - interpolation delay)
        render_time = time.time() - self.interpolation_delay
        
        # Find two snapshots to interpolate between
        snapshot_before = None
        snapshot_after = None
        
        for i in range(len(self.buffer) - 1):
            t1, state1 = self.buffer[i]
            t2, state2 = self.buffer[i + 1]
            
            if t1 <= render_time <= t2:
                snapshot_before = (t1, state1)
                snapshot_after = (t2, state2)
                break
        
        # If we didn't find a pair, use the two most recent
        if snapshot_before is None or snapshot_after is None:
            if len(self.buffer) >= 2:
                snapshot_before = self.buffer[-2]
                snapshot_after = self.buffer[-1]
            else:
                return self.buffer[-1][1] if self.buffer else None
        
        # Interpolate between the two snapshots
        return interpolate_states(snapshot_before, snapshot_after, render_time)


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values."""
    return a + (b - a) * t


def interpolate_states(
    snapshot_before: Tuple[float, dict],
    snapshot_after: Tuple[float, dict],
    render_time: float
) -> dict:
    """
    Interpolate between two game state snapshots.
    
    Args:
        snapshot_before: (timestamp, state) tuple for earlier state
        snapshot_after: (timestamp, state) tuple for later state
        render_time: time to render at
    
    Returns:
        Interpolated state dictionary
    """
    t1, state1 = snapshot_before
    t2, state2 = snapshot_after
    
    # Calculate interpolation factor
    if t2 == t1:
        alpha = 0.0
    else:
        alpha = (render_time - t1) / (t2 - t1)
        alpha = max(0.0, min(1.0, alpha))  # Clamp to [0, 1]
    
    # Create interpolated state
    interpolated_state = {
        "type": "state",
        "timestamp": render_time,
        "players": [],
        "coins": []
    }
    
    # Interpolate player positions
    players1 = {p["id"]: p for p in state1.get("players", [])}
    players2 = {p["id"]: p for p in state2.get("players", [])}
    
    for player_id in players2:
        if player_id in players1:
            p1 = players1[player_id]
            p2 = players2[player_id]
            
            interpolated_player = {
                "id": player_id,
                "x": lerp(p1["x"], p2["x"], alpha),
                "y": lerp(p1["y"], p2["y"], alpha),
                "vx": p2["vx"],
                "vy": p2["vy"],
                "score": p2["score"],
                "color": p2["color"],
                "radius": p2["radius"]
            }
            interpolated_state["players"].append(interpolated_player)
        else:
            # New player, just use the latest state
            interpolated_state["players"].append(players2[player_id])
    
    # Interpolate coin positions (coins don't move, so just use latest)
    coins2 = {c["id"]: c for c in state2.get("coins", [])}
    
    for coin_id, coin in coins2.items():
        interpolated_state["coins"].append(coin)
    
    return interpolated_state