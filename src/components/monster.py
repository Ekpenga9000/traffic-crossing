"""
Monster component for the traffic light logic gate game
Monsters roam back and forth at the bottom of the screen below the road
"""
import pygame
import random
import os
from ..utils.constants import *

class Monster:
    """
    Monty the monster that appears randomly at the bottom of the screen.
    Roams for a few seconds then disappears. Avoids appearing during pedestrian crossing.
    """
    
    def __init__(self, x, y, direction='right', speed=1, monster_type='monty'):
        """
        Initialize Monty the monster.
        
        Args:
            x (int): Initial X position
            y (int): Initial Y position
            direction (str): Direction of movement ('left' or 'right')
            speed (int): Speed of the monster in pixels per frame
            monster_type (str): Type of monster sprite to use
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.original_speed = speed
        self.monster_type = monster_type
        
        # Monster dimensions - 10x larger (5x * 2x)
        self.width = 480
        self.height = 480
        
        # Animation properties
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 15  # Frames between animation changes
        
        # Movement boundaries (stay at bottom of screen)
        self.left_boundary = 50
        self.right_boundary = SCREEN_WIDTH - 50
        
        # Appearance behavior - Start hidden
        self.state = 'hidden'  # 'hidden', 'appearing', 'roaming', 'disappearing'
        self.visibility_timer = 0
        self.roam_duration = 720  # Frames to roam (12 seconds at 60 FPS)
        self.hide_duration = 600  # Frames to stay hidden (10 seconds at 60 FPS)
        self.hide_timer = 0  # Track how long hidden
        self.crossing_guard_delay = 0  # Additional delay when crossing guard is active
        self.alpha = 0  # For fade in/out effects - Start hidden
        
        # Load monster sprites
        self.load_sprites()
        
        # Create rectangle for collision detection
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, self.width, self.height)
    
    def create_composite_monster(self):
        """Create a composite monster sprite from individual components.""" 
        if not self.sprite_components:
            self.sprites = None
            return
        
        # Create a surface to compose the monster
        monster_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Layer the components (order matters for proper layering)
        layer_order = ['leg', 'body', 'arm', 'eye', 'mouth']
        
        for component in layer_order:
            if component in self.sprite_components:
                sprite = self.sprite_components[component]
                
                # Scale sprite to fit our monster dimensions if needed
                sprite_rect = sprite.get_rect()
                if sprite_rect.width > self.width or sprite_rect.height > self.height:
                    # Scale down while maintaining aspect ratio
                    scale_factor = min(self.width / sprite_rect.width, self.height / sprite_rect.height)
                    new_width = int(sprite_rect.width * scale_factor)
                    new_height = int(sprite_rect.height * scale_factor)
                    sprite = pygame.transform.scale(sprite, (new_width, new_height))
                
                # Center the component on the monster surface
                component_rect = sprite.get_rect(center=(self.width//2, self.height//2))
                
                # Special positioning for different components
                if component == 'eye':
                    # Position eyes higher up
                    component_rect.centery = self.height//3
                elif component == 'mouth':
                    # Position mouth lower
                    component_rect.centery = int(self.height * 0.6)
                elif component == 'leg':
                    # Position legs at bottom
                    component_rect.centery = int(self.height * 0.8)
                elif component == 'arm':
                    # Position arms at middle sides
                    component_rect.centery = int(self.height * 0.5)
                
                monster_surface.blit(sprite, component_rect)
        
        # Store the composite monster
        self.sprites = {
            'idle': monster_surface,
            'walk1': monster_surface,  # For now, use same sprite
            'walk2': monster_surface   # Could add walking animation later
        }
    
    def load_sprites(self):
        """Load Little Axion monster sprites."""
        try:
            # Path to Little Axion sprite sheets
            sprite_path = os.path.join("assets", "sprites", "monsters", "monster", "Luneblade - Little Axion (Free)", "Sprite Sheet")
            print(f"DEBUG: Looking for sprites in: {sprite_path}")
            print(f"DEBUG: Sprite path exists: {os.path.exists(sprite_path)}")
            
            # Load different animation states
            self.sprite_sheets = {}
            
            # Load idle animation (main sprite for Monty)
            idle_path = os.path.join(sprite_path, "Idle.png")
            print(f"DEBUG: Idle path: {idle_path}, exists: {os.path.exists(idle_path)}")
            if os.path.exists(idle_path):
                self.sprite_sheets['idle'] = pygame.image.load(idle_path).convert_alpha()
                print(f"DEBUG: Loaded idle sprite: {self.sprite_sheets['idle'].get_size()}")
            
            # Load run animation for movement
            run_path = os.path.join(sprite_path, "Run.png")
            print(f"DEBUG: Run path: {run_path}, exists: {os.path.exists(run_path)}")
            if os.path.exists(run_path):
                self.sprite_sheets['run'] = pygame.image.load(run_path).convert_alpha()
                print(f"DEBUG: Loaded run sprite: {self.sprite_sheets['run'].get_size()}")
            
            # Load jump animation for appearing/disappearing
            jump_path = os.path.join(sprite_path, "Jump.png")
            print(f"DEBUG: Jump path: {jump_path}, exists: {os.path.exists(jump_path)}")
            if os.path.exists(jump_path):
                self.sprite_sheets['jump'] = pygame.image.load(jump_path).convert_alpha()
                print(f"DEBUG: Loaded jump sprite: {self.sprite_sheets['jump'].get_size()}")
            
            # Extract individual frames (assuming horizontal sprite sheet)
            self.sprites = {}
            frame_width = 144  # Actual frame width for Little Axion (matches height)
            frame_height = 144  # Actual frame height for Little Axion
            
            print(f"DEBUG: Processing {len(self.sprite_sheets)} sprite sheets")
            for animation, sheet in self.sprite_sheets.items():
                if sheet:
                    frames = []
                    sheet_width = sheet.get_width()
                    sheet_height = sheet.get_height()
                    num_frames = sheet_width // frame_width
                    
                    print(f"DEBUG: {animation} sheet size: {sheet_width}x{sheet_height}, frames: {num_frames}")
                    
                    for i in range(num_frames):
                        frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                        frame = sheet.subsurface(frame_rect).copy()
                        # Scale frame to match monster dimensions
                        scaled_frame = pygame.transform.scale(frame, (self.width, self.height))
                        frames.append(scaled_frame)
                    
                    self.sprites[animation] = frames
                    print(f"DEBUG: Created {len(frames)} frames for {animation}")
            
            # Set default sprites if loading succeeded
            if self.sprites:
                self.current_animation = 'run'  # TESTING: Start with run animation
                self.sprite_components = None  # Not using component system anymore
            else:
                raise Exception("No sprites loaded successfully")
            
        except Exception as e:
            print(f"Error loading Little Axion sprites: {e}")
            # Fallback to placeholder color - green for Monty
            self.color = (75, 150, 75)  # Green for Monty
            self.sprites = None
            self.sprite_components = None
    
    def update(self, dt, traffic_light):
        """
        Update monster behavior, animation, and position.
        
        Args:
            dt (float): Delta time since last frame
            traffic_light: Traffic light object to check pedestrian crossing status
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
        
        # Update state machine with proper timing and crossing guard awareness
        if self.state == 'hidden':
            self.hide_timer += 1
            
            # Check if crossing guard is active while hidden - add delay
            if traffic_light.is_green():
                self.crossing_guard_delay = 300  # Add 5 seconds delay (300 frames at 60 FPS)
            
            # Check if it's time to appear (including any crossing guard delay)
            total_hide_time = self.hide_duration + self.crossing_guard_delay
            if self.hide_timer >= total_hide_time:
                self.state = 'appearing'
                self.hide_timer = 0
                self.crossing_guard_delay = 0  # Reset delay
                self.current_animation = 'jump'  # Use jump animation for appearing
        
        elif self.state == 'appearing':
            self.alpha = min(255, self.alpha + 15)  # Fade in
            if self.alpha >= 255:
                self.state = 'roaming'
                self.visibility_timer = 0
                self.current_animation = 'run'
        
        elif self.state == 'roaming':
            self.visibility_timer += 1
            
            # Move around
            if self.direction == 'right':
                self.x += self.speed
                if self.x >= self.right_boundary:
                    self.direction = 'left'
                    self.x = self.right_boundary
            else:  # direction == 'left'
                self.x -= self.speed
                if self.x <= self.left_boundary:
                    self.direction = 'right'
                    self.x = self.left_boundary
            
            # Disappear after roaming for 5 seconds
            if self.visibility_timer >= self.roam_duration:
                self.state = 'disappearing'
                self.current_animation = 'jump'
                self.visibility_timer = 0
        
        elif self.state == 'disappearing':
            self.alpha = max(0, self.alpha - 15)  # Fade out
            if self.alpha <= 0:
                self.state = 'hidden'
                self.hide_timer = 0
                self.current_animation = 'idle'
        
        # Update rectangle position
        self.rect.centerx = self.x
        self.rect.centery = self.y
    
    def draw(self, surface):
        """
        Draw the monster on the surface with visibility states.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Don't draw if completely hidden
        if self.state == 'hidden':
            return
        
        if self.sprites and self.current_animation in self.sprites:
            # Draw Little Axion sprite with animation
            frames = self.sprites[self.current_animation]
            if frames:
                current_sprite = frames[self.animation_frame % len(frames)]
                
                # Flip sprite horizontally if moving left
                if self.direction == 'left':
                    current_sprite = pygame.transform.flip(current_sprite, True, False)
                
                # Apply alpha for fade in/out effects
                if self.alpha < 255:
                    fade_sprite = current_sprite.copy()
                    fade_sprite.set_alpha(self.alpha)
                    current_sprite = fade_sprite
                
                # Create position rectangle
                sprite_rect = current_sprite.get_rect()
                sprite_rect.centerx = self.x
                sprite_rect.centery = self.y
                
                # Draw the Little Axion sprite (no border)
                surface.blit(current_sprite, sprite_rect)
            
        else:
            # Fallback to placeholder colored rectangle with animation
            bounce_offset = 2 if self.animation_frame == 0 else -2
            
            # Calculate alpha for fade effects
            alpha_color = (*self.color, min(255, max(0, self.alpha)))
            
            # Create a surface for alpha blending
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Main body (no border)
            body_rect = pygame.Rect(0, bounce_offset, self.width, self.height)
            pygame.draw.rect(temp_surface, alpha_color, body_rect, border_radius=8)
            
            # Eyes
            eye_color = (*WHITE, self.alpha)
            pupil_color = (*BLACK, self.alpha)
            eye_size = 6
            pupil_size = 3
            
            # Left eye
            left_eye_pos = (self.width//2 - 12, self.height//2 - 8 + bounce_offset)
            pygame.draw.circle(temp_surface, eye_color, left_eye_pos, eye_size)
            pygame.draw.circle(temp_surface, pupil_color, left_eye_pos, pupil_size)
            
            # Right eye
            right_eye_pos = (self.width//2 + 12, self.height//2 - 8 + bounce_offset)
            pygame.draw.circle(temp_surface, eye_color, right_eye_pos, eye_size)
            pygame.draw.circle(temp_surface, pupil_color, right_eye_pos, pupil_size)
            
            # Simple mouth
            mouth_y = self.height//2 + 8 + bounce_offset
            if self.animation_frame == 0:
                # Closed mouth
                pygame.draw.line(temp_surface, (*BLACK, self.alpha), 
                               (self.width//2 - 8, mouth_y), (self.width//2 + 8, mouth_y), 3)
            else:
                # Open mouth (small oval)
                mouth_rect = pygame.Rect(self.width//2 - 6, mouth_y - 3, 12, 6)
                pygame.draw.ellipse(temp_surface, (*BLACK, self.alpha), mouth_rect)
            
            # Blit the temp surface to the main surface (no border)
            surface.blit(temp_surface, (self.x - self.width//2, self.y - self.height//2))
    
    def is_off_screen(self):
        """
        Check if monster is off screen (shouldn't happen with boundary checking).
        
        Returns:
            bool: Always False since monsters stay within boundaries
        """
        return False

class MonsterManager:
    """
    Manages Monty, the single monster roaming at the bottom of the screen.
    """
    
    def __init__(self, road_y, screen_width, screen_height):
        """
        Initialize the monster manager.
        
        Args:
            road_y (int): Y position of the road center
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.road_y = road_y
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Monster area is closer to the road
        self.monster_area_y = road_y + 120  # 120 pixels below the road center
        
        # Create Monty
        self.monty = self.create_monty()
    
    def create_monty(self):
        """Create Monty, our single monster character."""
        # Position Monty in the center-left area initially
        x = self.screen_width // 4
        y = self.monster_area_y
        direction = 'right'
        speed = 1.5  # Nice steady pace
        
        # Create Monty with a specific type (not random)
        monty = Monster(x, y, direction, speed, 'monty')
        return monty
    
    def update(self, dt, traffic_light):
        """
        Update Monty with traffic light awareness.
        
        Args:
            dt (float): Delta time since last frame
            traffic_light: Traffic light object to check pedestrian crossing status
        """
        self.monty.update(dt, traffic_light)
    
    def draw(self, surface):
        """
        Draw Monty.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        self.monty.draw(surface)
    
    def get_monty(self):
        """Get Monty monster instance."""
        return self.monty