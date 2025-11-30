import pytest
from server.game_state import GameState, PlayerState, Coin
from server.game_logic import (
    update_player_positions,
    set_player_velocity,
    check_collision,
    resolve_coin_collisions,
    spawn_coin,
    add_player,
    remove_player
)


def test_set_player_velocity():
    """Test setting player velocity based on direction."""
    player = PlayerState(id="test", x=100, y=100, speed=200)
    
    set_player_velocity(player, "up")
    assert player.vx == 0 and player.vy == -200
    
    set_player_velocity(player, "down")
    assert player.vx == 0 and player.vy == 200
    
    set_player_velocity(player, "left")
    assert player.vx == -200 and player.vy == 0
    
    set_player_velocity(player, "right")
    assert player.vx == 200 and player.vy == 0
    
    set_player_velocity(player, "stop")
    assert player.vx == 0 and player.vy == 0


def test_update_player_positions():
    """Test updating player positions based on velocity."""
    game_state = GameState(world_width=800, world_height=600)
    player = PlayerState(id="test", x=100, y=100, vx=100, vy=50)
    game_state.players["test"] = player
    
    # Update for 0.1 seconds
    update_player_positions(game_state, 0.1)
    
    assert player.x == 110  # 100 + 100 * 0.1
    assert player.y == 105  # 100 + 50 * 0.1


def test_update_player_positions_boundary_clamp():
    """Test that players are clamped to world boundaries."""
    game_state = GameState(world_width=800, world_height=600)
    player = PlayerState(id="test", x=10, y=10, vx=-200, vy=-200, radius=20)
    game_state.players["test"] = player
    
    # Update for 1 second (would move player outside boundaries)
    update_player_positions(game_state, 1.0)
    
    # Player should be clamped to radius distance from edge
    assert player.x == player.radius
    assert player.y == player.radius


def test_check_collision():
    """Test collision detection between two circular objects."""
    # Overlapping circles
    assert check_collision(0, 0, 10, 5, 0, 10) == True
    
    # Touching circles
    assert check_collision(0, 0, 10, 20, 0, 10) == False
    
    # Separate circles
    assert check_collision(0, 0, 10, 50, 0, 10) == False
    
    # Same position
    assert check_collision(0, 0, 10, 0, 0, 10) == True


def test_resolve_coin_collisions():
    """Test coin collection when player collides with coin."""
    game_state = GameState()
    
    # Add player at position (100, 100)
    player = PlayerState(id="test", x=100, y=100, radius=20, score=0)
    game_state.players["test"] = player
    
    # Add coin near player (will collide)
    coin1 = Coin(id="coin1", x=105, y=105, radius=10, value=5)
    game_state.coins.append(coin1)
    
    # Add coin far from player (won't collide)
    coin2 = Coin(id="coin2", x=500, y=500, radius=10, value=3)
    game_state.coins.append(coin2)
    
    # Resolve collisions
    collected = resolve_coin_collisions(game_state)
    
    # Check that coin1 was collected
    assert len(collected) == 1
    assert collected[0] == ("test", "coin1")
    
    # Check player score increased
    assert player.score == 5
    
    # Check coin1 was removed but coin2 remains
    assert len(game_state.coins) == 1
    assert game_state.coins[0].id == "coin2"


def test_spawn_coin():
    """Test spawning a coin in the game."""
    game_state = GameState(world_width=800, world_height=600)
    
    coin = spawn_coin(game_state)
    
    # Check coin was added to game state
    assert len(game_state.coins) == 1
    assert game_state.coins[0] == coin
    
    # Check coin is within boundaries
    assert 50 <= coin.x <= 750
    assert 50 <= coin.y <= 550
    
    # Check coin has valid value
    assert coin.value in [1, 2, 5]


def test_add_player():
    """Test adding a player to the game."""
    game_state = GameState(world_width=800, world_height=600)
    
    player = add_player(game_state, "player1")
    
    # Check player was added
    assert "player1" in game_state.players
    assert game_state.players["player1"] == player
    
    # Check player has valid initial position
    assert 100 <= player.x <= 700
    assert 100 <= player.y <= 500
    
    # Check player has default properties
    assert player.score == 0
    assert player.vx == 0
    assert player.vy == 0


def test_remove_player():
    """Test removing a player from the game."""
    game_state = GameState()
    
    # Add player
    add_player(game_state, "player1")
    assert "player1" in game_state.players
    
    # Remove player
    remove_player(game_state, "player1")
    assert "player1" not in game_state.players
    
    # Removing non-existent player should not raise error
    remove_player(game_state, "player2")


def test_multiple_players_coin_collision():
    """Test that only one player can collect a coin."""
    game_state = GameState()
    
    # Add two players near the same coin
    player1 = PlayerState(id="player1", x=100, y=100, radius=20, score=0)
    player2 = PlayerState(id="player2", x=110, y=110, radius=20, score=0)
    game_state.players["player1"] = player1
    game_state.players["player2"] = player2
    
    # Add coin between them
    coin = Coin(id="coin1", x=105, y=105, radius=10, value=10)
    game_state.coins.append(coin)
    
    # Resolve collisions
    collected = resolve_coin_collisions(game_state)
    
    # Only one player should have collected the coin
    assert len(collected) == 1
    assert len(game_state.coins) == 0
    
    # Check that only one player's score increased
    total_score = player1.score + player2.score
    assert total_score == 10