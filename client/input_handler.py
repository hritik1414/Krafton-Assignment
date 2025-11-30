import pygame
from typing import Optional


class InputHandler:
    """Handles keyboard input and converts it to game commands."""
    
    def __init__(self):
        self.current_move: Optional[str] = None
        self.last_sent_move: Optional[str] = None
    
    def process_input(self) -> Optional[str]:
        """
        Process keyboard input and return movement command if changed.
        Returns None if no change in input state.
        """
        keys = pygame.key.get_pressed()
        
        # Determine current movement based on keys
        new_move = None
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_move = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_move = "down"
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_move = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_move = "right"
        else:
            new_move = "stop"
        
        # Only return if movement changed
        if new_move != self.last_sent_move:
            self.last_sent_move = new_move
            return new_move
        
        return None
    
    def reset(self) -> None:
        """Reset input state."""
        self.current_move = None
        self.last_sent_move = None