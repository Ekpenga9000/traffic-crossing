"""
Pedestrian component for the traffic light logic gate game
Pedestrians walk on the sidewalk at the top side beside the road
"""
import pygame
import random
import os
from ..utils.constants import *

class Pedestrian:
    """
    A dino character that walks on the sidewalk beside the road.
    """
    
    def __init__(self, x, y, direction='right', speed=0.8):
        """
        Initialize a dino character.
        
        Args:
            x (int): Initial X position
            y (int): Initial Y position
            direction (str): Direction of movement ('left' or 'right')
            speed (float): Speed of the pedestrian in pixels per frame
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.original_speed = speed
        
        # Dino dimensions - made 1.5x smaller for better fit
        self.width = 63
        self.height = 63
        
        # Animation properties
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 20  # Frames between animation changes (slower than monster)
        
        # Movement boundaries (stay on sidewalk)
        self.left_boundary = -50  # Can go slightly off-screen
        self.right_boundary = SCREEN_WIDTH + 50  # Can go slightly off-screen
        
        # Current state
        self.state = 'walking'  # 'walking', 'idle'
        self.idle_timer = 0
        self.idle_duration = random.randint(60, 180)  # Random idle time
        
        # Load pedestrian sprites
        self.load_sprites()
        
        # Create rectangle for collision detection
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, self.width, self.height)
    
    def load_sprites(self):
        """Load dino sprites."""
        try:
            # Path to dino sprite sheets
            sprite_path = os.path.join("assets", "sprites", "dinos", "dinoCharactersVersion1.1", "sheets")
            
            # Load different animation states from different dino characters
            self.sprite_sheets = {}
            
            # Load doux (green dino) for walk animation
            doux_path = os.path.join(sprite_path, "DinoSprites - doux.png")
            if os.path.exists(doux_path):
                self.sprite_sheets['walk'] = pygame.image.load(doux_path).convert_alpha()
            
            # Load vita (blue dino) for idle animation  
            vita_path = os.path.join(sprite_path, "DinoSprites - vita.png")
            if os.path.exists(vita_path):
                self.sprite_sheets['idle'] = pygame.image.load(vita_path).convert_alpha()
            
            # Load mort (red dino) for run animation
            mort_path = os.path.join(sprite_path, "DinoSprites - mort.png")
            if os.path.exists(mort_path):
                self.sprite_sheets['run'] = pygame.image.load(mort_path).convert_alpha()
            
            # Extract individual frames from sprite sheets
            self.sprites = {}
            
            # Process sprite sheets into individual frames
            for animation, sheet in self.sprite_sheets.items():
                if sheet:
                    frames = []
                    sheet_width = sheet.get_width()  
                    sheet_height = sheet.get_height()
                    
                    # Calculate individual frame dimensions for dino sprites
                    # Dino sheets are 576x24, with 24 frames of 24x24 each
                    frame_width = 24
                    frame_height = 24
                    frame_count = sheet_width // frame_width
                    
                    # Extract individual frames
                    for i in range(frame_count):
                        # Create surface for individual frame
                        frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        source_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                        frame_surface.blit(sheet, (0, 0), source_rect)
                        
                        # Scale the individual frame to match pedestrian dimensions
                        scaled_frame = pygame.transform.scale(frame_surface, (self.width, self.height))
                        frames.append(scaled_frame)
                    
                    self.sprites[animation] = frames
            
            # Set default sprites if loading succeeded
            if self.sprites:
                self.current_animation = 'walk'
            else:
                raise Exception("No sprites loaded successfully")
            
        except Exception as e:
            print(f"Error loading dino sprites: {e}")
            # Fallback to placeholder color - green for dinos
            self.color = (50, 200, 100)  # Green for dinos
            self.sprites = None
    
    def update(self, dt):
        """
        Update dino behavior, animation, and position.
        
        Args:
            dt (float): Delta time since last frame
        """
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            if self.sprites and self.current_animation in self.sprites:
                num_frames = len(self.sprites[self.current_animation])
                self.animation_frame = (self.animation_frame + 1) % num_frames
            else:
                self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
        
        # Update behavior based on state
        if self.state == 'walking':
            # Move pedestrian
            if self.direction == 'right':
                self.x += self.speed
            else:  # direction == 'left'
                self.x -= self.speed
            
            # Randomly decide to stop and idle
            if random.randint(1, 300) == 1:  # 1 in 300 chance each frame
                self.state = 'idle'
                self.idle_timer = 0
                if self.sprites and 'idle' in self.sprites:
                    self.current_animation = 'idle'
        
        elif self.state == 'idle':
            self.idle_timer += 1
            if self.idle_timer >= self.idle_duration:
                self.state = 'walking'
                self.idle_duration = random.randint(60, 180)  # New random idle duration
                if self.sprites and 'walk' in self.sprites:
                    self.current_animation = 'walk'
        
        # Update rectangle position
        self.rect.centerx = self.x
        self.rect.centery = self.y
    
    def draw(self, surface):
        """
        Draw the dino on the surface.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        if self.sprites and self.current_animation in self.sprites:
            # Draw dino sprite with animation
            frames = self.sprites[self.current_animation]
            if frames:
                current_sprite = frames[self.animation_frame % len(frames)]
                
                # Flip sprite horizontally if moving left
                if self.direction == 'left':
                    current_sprite = pygame.transform.flip(current_sprite, True, False)
                
                # Create position rectangle
                sprite_rect = current_sprite.get_rect()
                sprite_rect.centerx = self.x
                sprite_rect.centery = self.y
                
                # Draw the dino sprite
                surface.blit(current_sprite, sprite_rect)
        else:
            # Fallback to placeholder colored rectangle with simple animation
            bounce_offset = 1 if self.animation_frame == 0 else -1
            
            # Main body
            body_rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2 + bounce_offset, 
                                  self.width, self.height)
            pygame.draw.rect(surface, self.color, body_rect, border_radius=4)
            pygame.draw.rect(surface, BLACK, body_rect, 1, border_radius=4)
            
            # Simple face
            eye_color = WHITE
            pupil_color = BLACK
            eye_size = 2
            
            # Eyes
            left_eye_pos = (self.x - 6, self.y - 8 + bounce_offset)
            right_eye_pos = (self.x + 6, self.y - 8 + bounce_offset)
            pygame.draw.circle(surface, eye_color, left_eye_pos, eye_size)
            pygame.draw.circle(surface, eye_color, right_eye_pos, eye_size)
            pygame.draw.circle(surface, pupil_color, left_eye_pos, 1)
            pygame.draw.circle(surface, pupil_color, right_eye_pos, 1)
    
    def is_off_screen(self):
        """
        Check if pedestrian is off screen and should be removed.
        
        Returns:
            bool: True if pedestrian is far off screen
        """
        return (self.x < self.left_boundary or self.x > self.right_boundary)

class PedestrianManager:
    """
    Manages pedestrians walking on the sidewalk beside the road.
    """
    
    def __init__(self, road_y, screen_width, screen_height):
        """
        Initialize the pedestrian manager.
        
        Args:
            road_y (int): Y position of the road center
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.road_y = road_y
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Sidewalk area is higher up, further from the road
        self.sidewalk_y = road_y - 140  # 140 pixels above the road center (lifted higher)
        
        # List of active pedestrians
        self.pedestrians = []
        
        # Spawn timing
        self.spawn_timer = 0
        self.spawn_interval = random.randint(120, 300)  # 2-5 seconds at 60 FPS
        
        # Create initial pedestrians
        self.spawn_initial_pedestrians()
    
    def spawn_initial_pedestrians(self):
        """Create a few initial pedestrians."""
        for _ in range(random.randint(2, 4)):
            self.spawn_pedestrian()
    
    def spawn_pedestrian(self):
        """Spawn a new pedestrian at a random edge of the screen."""
        # Randomly choose left or right side to spawn
        if random.choice([True, False]):
            # Spawn from left side, moving right
            x = -30
            direction = 'right'
        else:
            # Spawn from right side, moving left
            x = self.screen_width + 30
            direction = 'left'
        
        y = self.sidewalk_y
        speed = random.uniform(0.5, 1.2)  # Random walking speed
        
        pedestrian = Pedestrian(x, y, direction, speed)
        self.pedestrians.append(pedestrian)
    
    def update(self, dt):
        """
        Update all pedestrians.
        
        Args:
            dt (float): Delta time since last frame
        """
        # Update spawn timer
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_pedestrian()
            self.spawn_timer = 0
            self.spawn_interval = random.randint(120, 300)  # New random interval
        
        # Update all pedestrians
        for pedestrian in self.pedestrians[:]:  # Use slice copy for safe removal
            pedestrian.update(dt)
            
            # Remove pedestrians that are off screen
            if pedestrian.is_off_screen():
                self.pedestrians.remove(pedestrian)
    
    def draw(self, surface):
        """
        Draw all pedestrians.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        for pedestrian in self.pedestrians:
            pedestrian.draw(surface)
    
    def get_pedestrians(self):
        """Get list of all pedestrians."""
        return self.pedestrians