"""
TrafficLight component for the logic gate game
"""
import pygame
from ..utils.constants import *

class TrafficLight:
    """
    A traffic light that can display red, yellow, or green states.
    Used to visualize logic gate outputs.
    """
    
    def __init__(self, x, y, orientation='vertical'):
        """
        Initialize a traffic light.
        
        Args:
            x (int): X position of the traffic light
            y (int): Y position of the traffic light  
            orientation (str): 'vertical' or 'horizontal' orientation
        """
        self.x = x
        self.y = y
        self.orientation = orientation
        
        # Traffic light state
        self.red_on = True
        self.yellow_on = False
        self.green_on = False
        
        # Animation properties
        self.transition_alpha = 0.0
        self.target_alpha = 0.0
        self.animating = False
        
        # Calculate positions based on orientation (2 lights only: red and green)
        if orientation == 'vertical':
            self.box_rect = pygame.Rect(x - LIGHT_BOX_WIDTH//2, y - LIGHT_BOX_HEIGHT//2, 
                                      LIGHT_BOX_WIDTH, LIGHT_BOX_HEIGHT)
            self.red_pos = (x, y - 20)    # Top light (red)
            self.green_pos = (x, y + 20)  # Bottom light (green)
            self.pole_rect = pygame.Rect(x - LIGHT_POLE_WIDTH//2, y + LIGHT_BOX_HEIGHT//2,
                                       LIGHT_POLE_WIDTH, LIGHT_POLE_HEIGHT)
        else:  # horizontal
            self.box_rect = pygame.Rect(x - LIGHT_BOX_HEIGHT//2, y - LIGHT_BOX_WIDTH//2,
                                      LIGHT_BOX_HEIGHT, LIGHT_BOX_WIDTH)
            self.red_pos = (x - 20, y)    # Left light (red)
            self.green_pos = (x + 20, y)  # Right light (green)
            self.pole_rect = pygame.Rect(x + LIGHT_BOX_HEIGHT//2, y - LIGHT_POLE_WIDTH//2,
                                       LIGHT_POLE_HEIGHT, LIGHT_POLE_WIDTH)
    
    def set_state(self, red=False, yellow=False, green=False):
        """
        Set the traffic light state.
        
        Args:
            red (bool): Whether red light is on
            yellow (bool): Whether yellow light is on  
            green (bool): Whether green light is on
        """
        self.red_on = red
        self.yellow_on = yellow
        self.green_on = green
    
    def set_green(self):
        """Set traffic light to green (go)"""
        self.set_state(red=False, yellow=False, green=True)
    
    def set_red(self):
        """Set traffic light to red (stop)"""
        self.set_state(red=True, yellow=False, green=False)
    
    def set_yellow(self):
        """Set traffic light to yellow (caution)"""
        self.set_state(red=False, yellow=True, green=False)
    
    def update(self, dt):
        """
        Update traffic light animations.
        
        Args:
            dt (float): Delta time since last frame
        """
        # Update transition animations if needed
        if self.animating:
            self.transition_alpha += dt * 5  # Animation speed
            if self.transition_alpha >= 1.0:
                self.transition_alpha = 1.0
                self.animating = False
    
    def draw(self, surface):
        """
        Draw the traffic light on the surface.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Draw pole
        pygame.draw.rect(surface, DARK_GRAY, self.pole_rect)
        pygame.draw.rect(surface, BLACK, self.pole_rect, 2)
        
        # Draw traffic light box
        pygame.draw.rect(surface, BLACK, self.box_rect)
        pygame.draw.rect(surface, DARK_GRAY, self.box_rect, 3)
        
        # Draw lights (only red and green for pedestrian crossing)
        # Red light (top)
        red_color = RED if self.red_on else TRAFFIC_LIGHT_OFF
        pygame.draw.circle(surface, red_color, self.red_pos, LIGHT_RADIUS)
        pygame.draw.circle(surface, BLACK, self.red_pos, LIGHT_RADIUS, 2)
        
        # Green light (bottom) - skip yellow light for pedestrian crossing
        green_color = GREEN if self.green_on else TRAFFIC_LIGHT_OFF
        pygame.draw.circle(surface, green_color, self.green_pos, LIGHT_RADIUS)
        pygame.draw.circle(surface, BLACK, self.green_pos, LIGHT_RADIUS, 2)
    
    def is_green(self):
        """Check if traffic light is green"""
        return self.green_on
    
    def is_red(self):
        """Check if traffic light is red"""
        return self.red_on
    
    def is_yellow(self):
        """Check if traffic light is yellow"""
        return self.yellow_on