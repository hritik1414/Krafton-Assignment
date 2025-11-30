import pygame
from typing import Optional


class Renderer:
    """Handles rendering of the game state using Pygame."""
    
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Multiplayer Coin Collector")
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.coin_color = (255, 215, 0)  # Gold
        self.text_color = (255, 255, 255)
    
    def render(self, state: Optional[dict], player_id: Optional[str] = None) -> None:
        """Render the current game state."""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        if state is None:
            # Show waiting message
            text = self.font.render("Connecting to server...", True, self.text_color)
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            return
        
        # Draw coins
        for coin in state.get("coins", []):
            self.draw_coin(coin)
        
        # Draw players
        for player in state.get("players", []):
            is_local = player["id"] == player_id
            self.draw_player(player, is_local)
        
        # Draw scoreboard
        self.draw_scoreboard(state.get("players", []), player_id)
        
        # Draw FPS
        self.draw_fps()
        
        pygame.display.flip()
    
    def draw_player(self, player: dict, is_local: bool = False) -> None:
        """Draw a player circle."""
        x = int(player["x"])
        y = int(player["y"])
        radius = int(player["radius"])
        color = tuple(player["color"])
        
        # Draw player circle
        pygame.draw.circle(self.screen, color, (x, y), radius)
        
        # Draw outline for local player
        if is_local:
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius + 2, 2)
        
        # Draw player score above them
        score_text = self.small_font.render(str(player["score"]), True, self.text_color)
        score_rect = score_text.get_rect(center=(x, y - radius - 15))
        self.screen.blit(score_text, score_rect)
    
    def draw_coin(self, coin: dict) -> None:
        """Draw a coin."""
        x = int(coin["x"])
        y = int(coin["y"])
        radius = int(coin["radius"])
        
        # Draw coin with value indicator
        pygame.draw.circle(self.screen, self.coin_color, (x, y), radius)
        
        # Draw value text if > 1
        if coin.get("value", 1) > 1:
            value_text = self.small_font.render(str(coin["value"]), True, (0, 0, 0))
            value_rect = value_text.get_rect(center=(x, y))
            self.screen.blit(value_text, value_rect)
    
    def draw_scoreboard(self, players: list, player_id: Optional[str]) -> None:
        """Draw scoreboard in top-right corner."""
        y_offset = 10
        x_offset = self.width - 150
        
        # Title
        title = self.small_font.render("Scoreboard", True, self.text_color)
        self.screen.blit(title, (x_offset, y_offset))
        y_offset += 30
        
        # Sort players by score
        sorted_players = sorted(players, key=lambda p: p["score"], reverse=True)
        
        # Display top 5 players
        for i, player in enumerate(sorted_players[:5]):
            is_local = player["id"] == player_id
            color = (255, 255, 0) if is_local else self.text_color
            
            score_text = f"{i+1}. Score: {player['score']}"
            if is_local:
                score_text += " (You)"
            
            text = self.small_font.render(score_text, True, color)
            self.screen.blit(text, (x_offset, y_offset))
            y_offset += 25
    
    def draw_fps(self) -> None:
        """Draw FPS counter."""
        clock = pygame.time.Clock()
        fps = int(clock.get_fps())
        fps_text = self.small_font.render(f"FPS: {fps}", True, self.text_color)
        self.screen.blit(fps_text, (10, 10))
    
    def close(self) -> None:
        """Clean up and close the renderer."""
        pygame.quit()