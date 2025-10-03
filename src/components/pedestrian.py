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
        self.state = 'walking'  # 'walking', 'idle', 'wanting_to_cross', 'waiting_to_cross', 'crossing'
        self.idle_timer = 0
        self.idle_duration = random.randint(60, 180)  # Random idle time
        
        # Crossing behavior
        self.wants_to_cross = False
        self.crossing_wait_timer = 0
        self.crossing_target_y = 0  # Target Y position when crossing
        self.original_sidewalk_y = y  # Remember original sidewalk position
        self.is_waiting_at_crossing = False  # Track if waiting at zebra crossing
        
        # Zebra crossing navigation
        self.zebra_crossing_x = 0  # Will be set by manager
        self.zebra_crossing_width = 0  # Will be set by manager
        self.crossing_edge_tolerance = 10  # How close to crossing edge to stop
        
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
                        
                        # Store original frame for color changes
                        frames.append(scaled_frame)
                    
                    self.sprites[animation] = frames
            
            # Set default sprites if loading succeeded
            if self.sprites:
                self.current_animation = 'walk'
            else:
                raise Exception("No sprites loaded successfully")
            
        except Exception as e:
            print(f"Error loading dino sprites: {e}")
            # Fallback to placeholder color - blue for dinos
            self.color = (100, 150, 255)  # Blue for dinos
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
            
            # Randomly decide to go idle (crossing desire is now managed by PedestrianManager)
            if random.randint(1, 300) == 1:  # 1 in 300 chance to go idle
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
        
        elif self.state == 'wanting_to_cross':
            # Move toward the zebra crossing
            crossing_distance = abs(self.x - self.zebra_crossing_x)
            
            if crossing_distance > self.crossing_edge_tolerance:
                # Move toward zebra crossing
                if self.x < self.zebra_crossing_x:
                    self.x += self.speed
                    self.direction = 'right'
                else:
                    self.x -= self.speed
                    self.direction = 'left'
                
                # Use walk animation while moving to crossing
                if self.sprites and 'walk' in self.sprites:
                    self.current_animation = 'walk'
            else:
                # Reached the zebra crossing - start waiting
                self.state = 'waiting_to_cross'
                self.is_waiting_at_crossing = True
                if self.sprites and 'idle' in self.sprites:
                    self.current_animation = 'idle'
        
        elif self.state == 'waiting_to_cross':
            # Just wait at the crossing edge (yellow state handled in draw method)
            pass
        
        elif self.state == 'crossing':
            # Move vertically across the road to the opposite sidewalk
            if abs(self.y - self.crossing_target_y) > 2:  # Still crossing
                if self.y < self.crossing_target_y:
                    self.y += self.speed * 1.2  # Slightly faster crossing speed
                else:
                    self.y -= self.speed * 1.2
                
                # Use walk animation while crossing
                if self.sprites and 'walk' in self.sprites:
                    self.current_animation = 'walk'
            else:
                # Finished crossing - check if reached bottom sidewalk
                self.y = self.crossing_target_y  # Snap to exact position
                
                # Mark as completed crossing before potential removal
                self.state = 'crossing_completed'  # Special state for GameState to detect
                self.wants_to_cross = False
                self.is_waiting_at_crossing = False
        
        elif self.state == 'crossing_completed':
            # This state allows GameState to detect completion before removal
            # If pedestrian reached bottom sidewalk, mark for removal
            if self.crossing_target_y > self.original_sidewalk_y:  # Crossed from top to bottom
                return False  # Signal for removal
            
            # Otherwise resume normal walking on new sidewalk (shouldn't happen in current one-way system)
            self.state = 'walking'
            self.direction = random.choice(['left', 'right'])
            if self.sprites and 'walk' in self.sprites:
                self.current_animation = 'walk'
        
        # Update rectangle position
        self.rect.centerx = self.x
        self.rect.centery = self.y
        
        return True  # Continue existing (don't remove)
    
    def is_off_screen(self):
        """
        Check if pedestrian is off screen and should be removed.
        
        Returns:
            bool: True if off screen
        """
        return self.x < self.left_boundary or self.x > self.right_boundary
    
    def can_cross(self, crossing_guard_state):
        """
        Check if pedestrian can cross based on crossing guard state.
        
        Args:
            crossing_guard_state (str): Current state of crossing guard
            
        Returns:
            bool: True if pedestrian can cross
        """
        return crossing_guard_state == 'walk'  # Only cross when guard shows 'walk'
    
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
                current_sprite = frames[self.animation_frame % len(frames)].copy()
                
                # Apply color tint based on state
                if self.is_waiting_at_crossing:
                    # Apply yellow tint when waiting at crossing
                    yellow_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    yellow_overlay.fill((255, 255, 100, 128))  # Yellow with transparency
                    current_sprite.blit(yellow_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                else:
                    # Apply blue tint for normal state
                    blue_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    blue_overlay.fill((100, 150, 255, 128))  # Light blue with transparency
                    current_sprite.blit(blue_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                
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
    
    def __init__(self, road_y, screen_width, screen_height, zebra_crossing_x=None, zebra_crossing_width=None):
        """
        Initialize the pedestrian manager.
        
        Args:
            road_y (int): Y position of the road center
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
            zebra_crossing_x (int): X position of the zebra crossing center
            zebra_crossing_width (int): Width of the zebra crossing
        """
        self.road_y = road_y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zebra_crossing_x = zebra_crossing_x or screen_width // 2
        self.zebra_crossing_width = zebra_crossing_width or 100
        
        # Sidewalk areas
        self.top_sidewalk_y = road_y - 140  # Top sidewalk
        self.bottom_sidewalk_y = road_y + 140  # Bottom sidewalk
        self.sidewalk_y = self.top_sidewalk_y  # Default spawn location
        
        # List of active pedestrians
        self.pedestrians = []
        
        # Spawn timing
        self.spawn_timer = 0
        self.spawn_interval = random.randint(120, 300)  # 2-5 seconds at 60 FPS
        
        # Crossing timer - make pedestrians want to cross every 5 seconds
        self.crossing_timer = 0
        self.crossing_interval = 300  # 5 seconds at 60 FPS
        
        # Create initial pedestrians
        self.spawn_initial_pedestrians()
    
    def spawn_initial_pedestrians(self):
        """Create a few initial pedestrians."""
        for _ in range(random.randint(2, 4)):
            self.spawn_pedestrian()
    
    def spawn_pedestrian(self):
        """Spawn a new pedestrian at a random edge of the top sidewalk only."""
        # Randomly choose left or right side to spawn
        if random.choice([True, False]):
            # Spawn from left side, moving right
            x = -30
            direction = 'right'
        else:
            # Spawn from right side, moving left
            x = self.screen_width + 30
            direction = 'left'
        
        # Always spawn on top sidewalk only
        y = self.top_sidewalk_y
        speed = random.uniform(0.5, 1.2)  # Random walking speed
        
        pedestrian = Pedestrian(x, y, direction, speed)
        # Set zebra crossing coordinates
        pedestrian.zebra_crossing_x = self.zebra_crossing_x
        pedestrian.zebra_crossing_width = self.zebra_crossing_width
        self.pedestrians.append(pedestrian)
    
    def update(self, dt, crossing_guard_state='stop'):
        """
        Update all pedestrians.
        
        Args:
            dt (float): Delta time since last frame
            crossing_guard_state (str): Current crossing guard state
        """
        # Update spawn timer
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_pedestrian()
            self.spawn_timer = 0
            self.spawn_interval = random.randint(120, 300)  # New random interval
        
        # Update crossing timer - make a pedestrian want to cross every 5 seconds
        self.crossing_timer += 1
        if self.crossing_timer >= self.crossing_interval:
            self.trigger_crossing_desire()
            self.crossing_timer = 0
        
        # Update all pedestrians
        for pedestrian in self.pedestrians[:]:  # Use slice copy for safe removal
            # Allow crossing if guard permits and pedestrian is waiting
            if pedestrian.state == 'waiting_to_cross' and pedestrian.can_cross(crossing_guard_state):
                pedestrian.state = 'crossing'
                pedestrian.is_waiting_at_crossing = False  # No longer waiting
                # Set target to bottom sidewalk (one-way flow)
                pedestrian.crossing_target_y = self.bottom_sidewalk_y
                if pedestrian.sprites and 'walk' in pedestrian.sprites:
                    pedestrian.current_animation = 'walk'
            
            # Update pedestrian
            if not pedestrian.update(dt):
                # Remove pedestrian if update returns False (off-screen or finished crossing)
                self.pedestrians.remove(pedestrian)
    
    def draw(self, surface):
        """
        Draw all pedestrians.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        for pedestrian in self.pedestrians:
            pedestrian.draw(surface)
    
    def trigger_crossing_desire(self):
        """
        Make a pedestrian from the top sidewalk want to cross to the bottom.
        """
        # Find pedestrians on top sidewalk who are currently walking normally
        top_pedestrians = [
            p for p in self.pedestrians 
            if p.y < self.road_y and p.state == 'walking' and not p.wants_to_cross
        ]
        
        if top_pedestrians:
            # Choose a random pedestrian from the top sidewalk
            chosen_pedestrian = random.choice(top_pedestrians)
            chosen_pedestrian.wants_to_cross = True
            chosen_pedestrian.state = 'wanting_to_cross'
    
    def get_pedestrians(self):
        """Get list of all pedestrians."""
        return self.pedestrians