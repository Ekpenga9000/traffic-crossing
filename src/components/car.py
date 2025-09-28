"""
Car component for the traffic light logic gate game
"""
import pygame
import random
import os
from ..utils.constants import *

class Car:
    """
    A car that drives on the road and stops at red traffic lights.
    Used to demonstrate the effects of logic gate outputs on traffic flow.
    """
    
    def __init__(self, x, y, direction='right', speed=2, car_type=None):
        """
        Initialize a car.
        
        Args:
            x (int): Initial X position
            y (int): Initial Y position
            direction (str): Direction of travel ('left', 'right', 'up', 'down')
            speed (int): Speed of the car in pixels per frame
            car_type (str): Type of car sprite to use, random if None
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.original_speed = speed
        
        # Car appearance (2.25x bigger total: 1.5 * 1.5)
        self.width = 90  # 60 * 1.5 = 90 (originally 40 * 2.25)
        self.height = 45  # 30 * 1.5 = 45 (originally 20 * 2.25)
        self.car_type = car_type if car_type else self.random_car_type()
        self.color = self.random_car_color()  # Fallback color
        
        # Car state
        self.is_stopped = False
        self.stop_position = None
        
        # Load car sprite
        self.load_sprite()
        
        # Calculate car rectangle based on direction
        if direction in ['left', 'right']:
            self.rect = pygame.Rect(x, y - self.height // 2, self.width, self.height)
        else:  # up, down
            self.rect = pygame.Rect(x - self.width // 2, y, self.height, self.width)
    
    def random_car_type(self):
        """Select a random car type from available PixelCars sprites."""
        car_types = [
            '370z.png', '500x.png', 'A4.png', 'Beetle.png', 'Corolla.png', 
            'DB9.png', 'F1.png', 'FType.png', 'Giulia.png', 'Giulietta.png',
            'Jimny.png', 'Logan.png', 'Polo.png', 'RSeries.png', 'Sandero.png',
            'Tipo.png', 'VNL300.png', 'Viper.png'
        ]
        return random.choice(car_types)
    
    def random_car_color(self):
        """Generate a random car color for fallback."""
        colors = [
            (255, 100, 100),  # Red
            (100, 100, 255),  # Blue
            (100, 255, 100),  # Green
            (255, 255, 100),  # Yellow
            (255, 150, 100),  # Orange
            (150, 100, 255),  # Purple
            (100, 255, 255),  # Cyan
            (255, 100, 255),  # Magenta
            (150, 150, 150),  # Gray
            (100, 50, 0),     # Brown
        ]
        return random.choice(colors)
    
    def load_sprite(self):
        """Load the car sprite from the PixelCars assets folder."""
        try:
            # Path to PixelCars sprites
            sprite_path = os.path.join("assets", "sprites", "cars", "PixelCars", "sprite", self.car_type)
            
            if os.path.exists(sprite_path):
                # Load the sprite
                original_sprite = pygame.image.load(sprite_path).convert_alpha()
                
                # Rotate the sprite by 90 degrees to the right (clockwise)
                rotated_sprite = pygame.transform.rotate(original_sprite, -90)
                
                # Make the sprite 2x larger
                original_size = rotated_sprite.get_size()
                enlarged_sprite = pygame.transform.scale(rotated_sprite, (original_size[0] * 2, original_size[1] * 2))
                
                # Scale sprite to fit our car dimensions while maintaining aspect ratio
                sprite_rect = enlarged_sprite.get_rect()
                scale_factor = min(self.width / sprite_rect.width, self.height / sprite_rect.height)
                
                if scale_factor != 1.0:
                    new_width = int(sprite_rect.width * scale_factor)
                    new_height = int(sprite_rect.height * scale_factor)
                    self.sprite = pygame.transform.scale(enlarged_sprite, (new_width, new_height))
                else:
                    self.sprite = enlarged_sprite
                
                # Update car dimensions to match sprite
                self.width = self.sprite.get_width()
                self.height = self.sprite.get_height()
                
            else:
                print(f"PixelCars sprite not found: {sprite_path}")
                self.sprite = None
                
        except Exception as e:
            print(f"Error loading PixelCars sprite: {e}")
            self.sprite = None
    
    def update(self, dt, traffic_light, zebra_crossing_x, zebra_crossing_width, other_cars=None):
        """
        Update car position and behavior.
        
        Args:
            dt (float): Delta time since last frame
            traffic_light: Traffic light object to check state
            zebra_crossing_x (int): X position of zebra crossing center
            zebra_crossing_width (int): Width of zebra crossing
            other_cars (list): List of other cars to check for collisions
        """
        if other_cars is None:
            other_cars = []
            
        # Check if car should stop at zebra crossing
        crossing_left = zebra_crossing_x - zebra_crossing_width // 2
        crossing_right = zebra_crossing_x + zebra_crossing_width // 2
        
        # Determine if car is approaching the crossing
        if self.direction == 'right':
            approaching_crossing = (self.rect.right >= crossing_left - 50 and 
                                  self.rect.left <= crossing_left)
            direction_multiplier = 1
        elif self.direction == 'left':
            approaching_crossing = (self.rect.left <= crossing_right + 50 and 
                                  self.rect.right >= crossing_right)
            direction_multiplier = -1
        else:
            approaching_crossing = False
            direction_multiplier = 0
        
        # Check if pedestrians are crossing (green pedestrian light)
        pedestrians_crossing = traffic_light.is_green()
        
        # Check for car-to-car collision (stop behind other cars)
        car_ahead = False
        safe_distance = 50  # Minimum distance to maintain from car ahead
        
        for other_car in other_cars:
            if other_car == self:  # Skip self
                continue
                
            # Check if other car is in the same lane and ahead of this car
            if abs(other_car.y - self.y) < 15:  # Same lane (within 15 pixels)
                if self.direction == 'right':
                    # Check if other car is ahead (to the right) and close
                    if (other_car.rect.left > self.rect.right and 
                        other_car.rect.left - self.rect.right < safe_distance):
                        car_ahead = True
                        break
                elif self.direction == 'left':
                    # Check if other car is ahead (to the left) and close
                    if (other_car.rect.right < self.rect.left and 
                        self.rect.left - other_car.rect.right < safe_distance):
                        car_ahead = True
                        break
        
        # Stop if pedestrians are crossing and approaching, OR if there's a car ahead
        if (pedestrians_crossing and approaching_crossing) or car_ahead:
            self.is_stopped = True
            self.speed = 0
        else:
            self.is_stopped = False
            self.speed = self.original_speed
        
        # Update position
        if self.direction == 'right':
            self.x += self.speed
            self.rect.x = self.x
        elif self.direction == 'left':
            self.x -= self.speed
            self.rect.x = self.x
        elif self.direction == 'up':
            self.y -= self.speed
            self.rect.y = self.y
        elif self.direction == 'down':
            self.y += self.speed
            self.rect.y = self.y
    
    def draw(self, surface):
        """
        Draw the car on the surface using sprite or fallback to rectangle.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        if self.sprite:
            # Draw the actual car sprite
            current_sprite = self.sprite
            
            # Flip sprite horizontally if moving left
            if self.direction == 'left':
                current_sprite = pygame.transform.flip(self.sprite, True, False)
            
            # Center the sprite in the car's rectangle
            sprite_rect = current_sprite.get_rect()
            sprite_rect.center = self.rect.center
            
            surface.blit(current_sprite, sprite_rect)
            
        else:
            # Fallback to drawing rectangles if sprite fails to load
            # Draw main car body
            pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
            pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=4)  # Border
            
            # Draw windshield (lighter color at the front)
            windshield_color = tuple(min(255, c + 40) for c in self.color)  # Lighter shade
            if self.direction == 'right':
                windshield_rect = pygame.Rect(self.rect.right - 12, self.rect.y + 4, 9, self.rect.height - 8)
            else:  # Moving left
                windshield_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 4, 9, self.rect.height - 8)
            pygame.draw.rect(surface, windshield_color, windshield_rect, border_radius=3)
            
            # Draw side windows
            window_color = (150, 200, 255)  # Light blue for windows
            window_height = 6  # Scaled up from 4
            window_y_top = self.rect.y + 3
            window_y_bottom = self.rect.bottom - 9
            
            # Top and bottom windows
            window_rect_top = pygame.Rect(self.rect.x + 12, window_y_top, self.rect.width - 24, window_height)
            window_rect_bottom = pygame.Rect(self.rect.x + 12, window_y_bottom, self.rect.width - 24, window_height)
            pygame.draw.rect(surface, window_color, window_rect_top)
            pygame.draw.rect(surface, window_color, window_rect_bottom)
    
    def is_off_screen(self, screen_width, screen_height):
        """
        Check if the car has moved off screen.
        
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
            
        Returns:
            bool: True if car is off screen
        """
        if self.direction == 'right':
            return self.rect.left > screen_width
        elif self.direction == 'left':
            return self.rect.right < 0
        elif self.direction == 'up':
            return self.rect.bottom < 0
        elif self.direction == 'down':
            return self.rect.top > screen_height
        return False

class CarManager:
    """
    Manages multiple cars and their spawning.
    """
    
    def __init__(self, road_y, screen_width):
        """
        Initialize the car manager.
        
        Args:
            road_y (int): Y position of the road center
            screen_width (int): Width of the screen
        """
        self.cars = []
        self.road_y = road_y
        self.screen_width = screen_width
        self.spawn_timer = 0
        self.spawn_interval = 180  # Spawn every 3 seconds at 60 FPS
    
    def update(self, dt, traffic_light, zebra_crossing_x, zebra_crossing_width):
        """
        Update all cars and handle spawning.
        
        Args:
            dt (float): Delta time since last frame
            traffic_light: Traffic light object
            zebra_crossing_x (int): X position of zebra crossing center
            zebra_crossing_width (int): Width of zebra crossing
        """
        # Update existing cars with collision detection
        for car in self.cars[:]:  # Use slice to avoid modification during iteration
            car.update(dt, traffic_light, zebra_crossing_x, zebra_crossing_width, self.cars)
            
            # Remove cars that are off screen
            if car.is_off_screen(self.screen_width, 600):  # Assuming height of 600
                self.cars.remove(car)
        
        # Handle car spawning
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_car()
            self.spawn_timer = 0
    
    def spawn_car(self):
        """Spawn a new car from either side of the screen on appropriate lanes."""
        # Randomly choose direction
        if random.choice([True, False]):
            # Spawn from left, moving right (bottom lane)
            x = -50
            y = self.road_y + 25  # Bottom half of the road
            direction = 'right'
        else:
            # Spawn from right, moving left (top lane)
            x = self.screen_width + 50
            y = self.road_y - 25  # Top half of the road
            direction = 'left'
        
        # Create new car (car_type will be selected randomly)
        new_car = Car(x, y, direction, random.randint(2, 4))
        self.cars.append(new_car)
    
    def draw(self, surface):
        """
        Draw all cars.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        for car in self.cars:
            car.draw(surface)
    
    def get_car_count(self):
        """Get the current number of cars on screen."""
        return len(self.cars)