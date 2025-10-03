"""
CrossingGuard component for the logic gate game
Replaces the traffic light with a dino crossing guard sprite
"""
import pygame
import os
from ..utils.constants import *

class CrossingGuard:
    """
    A dino crossing guard that can signal stop or go to control traffic.
    Used to visualize logic gate outputs with cute dino sprites.
    """
    
    def __init__(self, x, y):
        """
        Initialize a dino crossing guard.
        
        Args:
            x (int): X position of the crossing guard
            y (int): Y position of the crossing guard
        """
        self.x = x
        self.y = y
        
        # Guard state
        self.is_stopping_traffic = True  # True = stop traffic (red equivalent), False = allow traffic (green equivalent)
        
        # Animation properties
        self.transition_alpha = 0.0
        self.target_alpha = 0.0
        self.animating = False
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Load dino sprite sheet
        self.load_sprites()
        
        # Sprite dimensions (will be set after loading sprites)
        self.width = 64
        self.height = 64
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, self.width, self.height)
    
    def load_sprites(self):
        """Load dino sprite sheet and extract individual frames."""
        try:
            # Path to the dino sprite sheet (using doux - the green dino)
            sprite_path = os.path.join("assets", "sprites", "dinos", "dinoCharactersVersion1.1", "sheets", "DinoSprites - doux.png")
            
            # Load the sprite sheet
            if os.path.exists(sprite_path):
                self.sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                
                # Extract individual sprites from the sheet
                # Assuming each sprite is 24x24 pixels (common for pixel art)
                sprite_size = 24
                self.sprites = {}
                
                # Extract idle sprite (first frame, top-left)
                self.sprites['idle'] = self.sprite_sheet.subsurface(pygame.Rect(0, 0, sprite_size, sprite_size))
                
                # Extract different animation frames for variety
                # Walking animation for "go" state
                self.sprites['walk1'] = self.sprite_sheet.subsurface(pygame.Rect(sprite_size, 0, sprite_size, sprite_size))
                self.sprites['walk2'] = self.sprite_sheet.subsurface(pygame.Rect(sprite_size * 2, 0, sprite_size, sprite_size))
                
                # Use idle for stop state, walking for go state
                self.sprites['stop'] = self.sprites['walk1']
                self.sprites['go1'] = self.sprites['walk1'] 
                self.sprites['go2'] = self.sprites['walk2']
                
                # Scale up the sprites for better visibility
                scale_factor = 3
                for key in self.sprites:
                    original = self.sprites[key]
                    scaled = pygame.transform.scale(original, (sprite_size * scale_factor, sprite_size * scale_factor))
                    self.sprites[key] = scaled
                
                self.width = sprite_size * scale_factor
                self.height = sprite_size * scale_factor
                
            else:
                # Fallback to None if sprite not found
                self.sprite_sheet = None
                self.sprites = None
                print(f"Warning: Dino sprite not found at {sprite_path}")
                
        except Exception as e:
            print(f"Error loading dino sprites: {e}")
            self.sprite_sheet = None
            self.sprites = None
        
    def set_stop(self):
        """Set crossing guard to stop traffic (equivalent to red light)"""
        self.is_stopping_traffic = True
    
    def set_go(self):
        """Set crossing guard to allow traffic (equivalent to green light)"""
        self.is_stopping_traffic = False
    
    def set_red(self):
        """Compatibility method - set to stop traffic"""
        self.set_stop()
    
    def set_green(self):
        """Compatibility method - set to allow traffic"""
        self.set_go()
        
    def is_red(self):
        """Compatibility method - check if stopping traffic"""
        return self.is_stopping_traffic
    
    def is_green(self):
        """Compatibility method - check if allowing traffic"""
        return not self.is_stopping_traffic
    
    def is_yellow(self):
        """Compatibility method - crossing guard doesn't have yellow state"""
        return False
    
    def update(self, dt):
        """
        Update dino crossing guard animations.
        
        Args:
            dt (float): Delta time since last frame
        """
        # Update transition animations if needed
        if self.animating:
            self.transition_alpha += dt * 5  # Animation speed
            if self.transition_alpha >= 1.0:
                self.transition_alpha = 1.0
                self.animating = False
        
        # Update walking animation when in "go" state
        if not self.is_stopping_traffic:
            self.animation_timer += dt * 60  # Convert to frame-based timing
            if self.animation_timer >= 30:  # Change frame every 30 game frames
                self.animation_frame = (self.animation_frame + 1) % 2  # Toggle between 0 and 1
                self.animation_timer = 0
    
    def draw(self, surface):
        """
        Draw the dino crossing guard sprite on the surface.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        if self.sprites is None:
            # Fallback to simple colored rectangle if sprites failed to load
            fallback_rect = pygame.Rect(self.x - 16, self.y - 16, 32, 32)
            pygame.draw.rect(surface, GREEN, fallback_rect)
            pygame.draw.rect(surface, BLACK, fallback_rect, 2)
            
            # Add simple text indicator
            font = pygame.font.Font(None, 24)
            text = "DINO" if self.is_stopping_traffic else "GO"
            text_surface = font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=(self.x, self.y + 25))
            surface.blit(text_surface, text_rect)
            return
        
        # Draw the appropriate dino sprite based on state
        if self.is_stopping_traffic:
            # Use idle sprite for stop state
            current_sprite = self.sprites['stop']
        else:
            # Use animated walking sprites for go state
            if self.animation_frame == 0:
                current_sprite = self.sprites['go1']
            else:
                current_sprite = self.sprites['go2']
        
        # Draw the dino sprite centered at the guard position
        sprite_rect = current_sprite.get_rect()
        sprite_rect.center = (self.x, self.y)
        surface.blit(current_sprite, sprite_rect)
        
        # Add visual indicators for the traffic control state
        if self.is_stopping_traffic:
            # Draw octagonal stop sign above the dino with increased padding
            stop_sign_center = (self.x + 30, self.y - 30)
            octagon_radius = 25  # Increased from 24 for more padding around text
            
            # Create octagon points
            import math
            octagon_points = []
            for i in range(8):
                angle = i * math.pi / 4  # 45 degrees between each point
                x = stop_sign_center[0] + octagon_radius * math.cos(angle)
                y = stop_sign_center[1] + octagon_radius * math.sin(angle)
                octagon_points.append((x, y))
            
            # Draw filled octagon
            pygame.draw.polygon(surface, RED, octagon_points)
            pygame.draw.polygon(surface, BLACK, octagon_points, 3)  # Black border
            
            # STOP text on sign (slightly smaller font for better proportions)
            font = pygame.font.Font(None, 20)
            stop_text = font.render("STOP", True, WHITE)
            stop_rect = stop_text.get_rect(center=stop_sign_center)
            surface.blit(stop_text, stop_rect)
        else:
            # Draw larger GO indicator with motion lines
            go_center = (self.x + 30, self.y - 30)
            pygame.draw.circle(surface, GREEN, go_center, 18)
            pygame.draw.circle(surface, BLACK, go_center, 18, 2)
            
            # GO text (larger font)
            font = pygame.font.Font(None, 26)
            go_text = font.render("GO", True, WHITE)
            go_rect = go_text.get_rect(center=go_center)
            surface.blit(go_text, go_rect)
            
            # Motion lines to indicate movement
            pygame.draw.line(surface, GRAY, (self.x - 40, self.y - 20), (self.x - 25, self.y - 15), 2)
            pygame.draw.line(surface, GRAY, (self.x - 38, self.y - 15), (self.x - 23, self.y - 10), 2)
            pygame.draw.line(surface, GRAY, (self.x - 36, self.y - 10), (self.x - 21, self.y - 5), 2)