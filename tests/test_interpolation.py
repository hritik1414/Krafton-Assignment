import pytest
import time
from client.interpolation import StateBuffer, lerp, interpolate_states


def test_lerp():
    """Test linear interpolation function."""
    assert lerp(0, 10, 0.0) == 0
    assert lerp(0, 10, 1.0) == 10
    assert lerp(0, 10, 0.5) == 5
    assert lerp(100, 200, 0.25) == 125
    assert lerp(-10, 10, 0.5) == 0


def test_state_buffer_add_snapshot():
    """Test adding snapshots to the buffer."""
    buffer = StateBuffer(max_size=5)
    
    state1 = {"players": [], "coins": []}
    state2 = {"players": [], "coins": []}
    
    buffer.add_snapshot(1.0, state1)
    buffer.add_snapshot(2.0, state2)
    
    assert len(buffer.buffer) == 2


def test_state_buffer_max_size():
    """Test that buffer respects max size."""
    buffer = StateBuffer(max_size=3)
    
    for i in range(5):
        state = {"players": [], "coins": []}
        buffer.add_snapshot(float(i), state)
    
    # Should only keep last 3
    assert len(buffer.buffer) == 3
    assert buffer.buffer[0][0] == 2.0
    assert buffer.buffer[-1][0] == 4.0


def test_interpolate_states_players():
    """Test interpolating player positions between two states."""
    state1 = {
        "players": [
            {"id": "p1", "x": 100, "y": 100, "vx": 10, "vy": 0, "score": 5, "color": [255, 0, 0], "radius": 20}
        ],
        "coins": []
    }
    
    state2 = {
        "players": [
            {"id": "p1", "x": 200, "y": 100, "vx": 10, "vy": 0, "score": 5, "color": [255, 0, 0], "radius": 20}
        ],
        "coins": []
    }
    
    # Interpolate at 50% between states
    snapshot1 = (1.0, state1)
    snapshot2 = (2.0, state2)
    render_time = 1.5
    
    result = interpolate_states(snapshot1, snapshot2, render_time)
    
    # Player should be at midpoint
    assert result["players"][0]["x"] == 150
    assert result["players"][0]["y"] == 100
    assert result["players"][0]["score"] == 5


def test_interpolate_states_alpha_clamping():
    """Test that interpolation alpha is clamped to [0, 1]."""
    state1 = {
        "players": [
            {"id": "p1", "x": 100, "y": 100, "vx": 0, "vy": 0, "score": 0, "color": [255, 0, 0], "radius": 20}
        ],
        "coins": []
    }
    
    state2 = {
        "players": [
            {"id": "p1", "x": 200, "y": 200, "vx": 0, "vy": 0, "score": 0, "color": [255, 0, 0], "radius": 20}
        ],
        "coins": []
    }
    
    snapshot1 = (1.0, state1)
    snapshot2 = (2.0, state2)
    
    # Render time before first snapshot
    result = interpolate_states(snapshot1, snapshot2, 0.5)
    assert result["players"][0]["x"] == 100  # Should use state1
    
    # Render time after second snapshot
    result = interpolate_states(snapshot1, snapshot2, 2.5)
    assert result["players"][0]["x"] == 200  # Should use state2


def test_interpolate_states_new_player():
    """Test handling of a player that only exists in the second state."""
    state1 = {
        "players": [],
        "coins": []
    }
    
    state2 = {
        "players": [
            {"id": "p1", "x": 100, "y": 100, "vx": 0, "vy": 0, "score": 0, "color": [255, 0, 0], "radius": 20}
        ],
        "coins": []
    }
    
    snapshot1 = (1.0, state1)
    snapshot2 = (2.0, state2)
    
    result = interpolate_states(snapshot1, snapshot2, 1.5)
    
    # New player should appear at their position in state2
    assert len(result["players"]) == 1
    assert result["players"][0]["x"] == 100


def test_interpolate_states_coins():
    """Test that coins are taken from the later state (no interpolation needed)."""
    state1 = {
        "players": [],
        "coins": [
            {"id": "c1", "x": 100, "y": 100, "value": 1, "radius": 10}
        ]
    }
    
    state2 = {
        "players": [],
        "coins": [
            {"id": "c1", "x": 100, "y": 100, "value": 1, "radius": 10},
            {"id": "c2", "x": 200, "y": 200, "value": 5, "radius": 10}
        ]
    }
    
    snapshot1 = (1.0, state1)
    snapshot2 = (2.0, state2)
    
    result = interpolate_states(snapshot1, snapshot2, 1.5)
    
    # Should have coins from state2
    assert len(result["coins"]) == 2


def test_state_buffer_get_interpolated_state_insufficient_data():
    """Test that buffer returns None when insufficient snapshots."""
    buffer = StateBuffer()
    
    # No snapshots
    assert buffer.get_interpolated_state() is None
    
    # Only one snapshot
    buffer.add_snapshot(1.0, {"players": [], "coins": []})
    assert buffer.get_interpolated_state() is None


def test_state_buffer_get_interpolated_state():
    """Test getting interpolated state from buffer."""
    buffer = StateBuffer(interpolation_delay=0.1)
    
    current_time = time.time()
    
    # Add snapshots
    state1 = {
        "players": [
            {"id": "p1", "x": 100, "y": 100, "vx": 0, "vy": 0, "score": 0, "color": [255, 0, 0], "radius": 20}
        ],
        "coins": []
    }
    
    state2 = {
        "players": [
            {"id": "p1", "x": 200, "y": 200, "vx": 0, "vy": 0, "score": 0, "color": [255, 0, 0], "radius": 20}
        ],
        "coins": []
    }
    
    buffer.add_snapshot(current_time - 0.2, state1)
    buffer.add_snapshot(current_time - 0.05, state2)
    
    result = buffer.get_interpolated_state()
    
    # Should return an interpolated state
    assert result is not None
    assert "players" in result
    assert len(result["players"]) == 1


def test_interpolate_multiple_players():
    """Test interpolating multiple players at once."""
    state1 = {
        "players": [
            {"id": "p1", "x": 0, "y": 0, "vx": 0, "vy": 0, "score": 0, "color": [255, 0, 0], "radius": 20},
            {"id": "p2", "x": 100, "y": 100, "vx": 0, "vy": 0, "score": 5, "color": [0, 255, 0], "radius": 20}
        ],
        "coins": []
    }
    
    state2 = {
        "players": [
            {"id": "p1", "x": 100, "y": 100, "vx": 0, "vy": 0, "score": 2, "color": [255, 0, 0], "radius": 20},
            {"id": "p2", "x": 200, "y": 200, "vx": 0, "vy": 0, "score": 7, "color": [0, 255, 0], "radius": 20}
        ],
        "coins": []
    }
    
    snapshot1 = (1.0, state1)
    snapshot2 = (2.0, state2)
    
    # Interpolate at 25%
    result = interpolate_states(snapshot1, snapshot2, 1.25)
    
    assert len(result["players"]) == 2
    
    # Find each player
    p1 = next(p for p in result["players"] if p["id"] == "p1")
    p2 = next(p for p in result["players"] if p["id"] == "p2")
    
    # Check p1 interpolation (0.25 between 0 and 100)
    assert p1["x"] == 25
    assert p1["y"] == 25
    assert p1["score"] == 2  # Score doesn't interpolate
    
    # Check p2 interpolation (0.25 between 100 and 200)
    assert p2["x"] == 125
    assert p2["y"] == 125
    assert p2["score"] == 7