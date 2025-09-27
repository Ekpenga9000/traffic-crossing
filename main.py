"""
Main game file for the Traffic Light Logic Gate Game
"""
import pygame
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.constants import *
from src.components.road import Road, Intersection
from src.components.traffic_light import TrafficLight

class TrafficLightGame:
    """
    Main game class that manages the traffic light logic gate educational game.
    """
    
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Traffic Light Logic Gate Game")
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        
        # Initialize game objects
        self.setup_scene()
    
    def setup_scene(self):
        """Set up the initial scene with a single road, zebra crossing, and pedestrian traffic light."""
        # Create a single horizontal road across the screen
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Single horizontal road (east-west) with zebra crossing
        self.road = Road(
            start_x=50, 
            start_y=center_y,
            end_x=SCREEN_WIDTH - 50,
            end_y=center_y,
            num_lanes=2
        )
        
        # Zebra crossing position (center of the screen)
        self.zebra_crossing_x = center_x
        self.zebra_crossing_width = 100
        
        # Create traffic light
        self.traffic_lights = []
        
        # Pedestrian traffic light (only red and green, no yellow)
        self.pedestrian_light = TrafficLight(
            x=center_x + 80,                                  # Moved horizontally by 5rem (~80px)
            y=center_y - ROAD_WIDTH//2 - 150,                 # On the side of the road, away from crossing
            orientation='vertical'
        )
        self.pedestrian_light.set_red()  # Start with red (pedestrians wait)
        self.traffic_lights.append(self.pedestrian_light)
    
    def handle_events(self):
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Toggle traffic lights when space is pressed
                    self.toggle_traffic_lights()
    
    def toggle_traffic_lights(self):
        """Toggle the pedestrian traffic light state."""
        # Simple toggle between red and green for pedestrian crossing
        if self.pedestrian_light.is_red():
            self.pedestrian_light.set_green()  # Allow pedestrians to cross
        else:
            self.pedestrian_light.set_red()    # Stop pedestrians
    
    def update(self, dt):
        """
        Update game state.
        
        Args:
            dt (float): Delta time since last frame
        """
        # Update traffic lights
        for light in self.traffic_lights:
            light.update(dt)
    
    def draw(self):
        """Draw the game."""
        # Clear screen with background color
        self.screen.fill(WHITE)
        
        # Draw the single road
        self.road.draw(self.screen)
        
        # Draw zebra crossing
        self.draw_zebra_crossing()
        
        # Draw traffic lights
        for light in self.traffic_lights:
            light.draw(self.screen)
        
        # Draw labels for traffic lights
        self.draw_traffic_light_labels()
        
        # Draw instructions
        self.draw_instructions()
        
        # Update display
        pygame.display.flip()
    
    def draw_zebra_crossing(self):
        """Draw the zebra crossing on the road."""
        # Zebra crossing stripes (white stripes on dark background) - fewer, broader stripes
        stripe_height = 20  # Much broader stripes
        stripe_spacing = 30  # More space between stripes
        num_stripes = 6     # Reduced number of stripes to fit road width better
        
        # Draw dark background for crossing
        crossing_rect = pygame.Rect(
            self.zebra_crossing_x - self.zebra_crossing_width // 2,
            SCREEN_HEIGHT // 2 - ROAD_WIDTH // 2,
            self.zebra_crossing_width,
            ROAD_WIDTH
        )
        pygame.draw.rect(self.screen, BLACK, crossing_rect)
        
        # Calculate starting position to center the stripes
        total_stripe_area = (num_stripes * stripe_height) + ((num_stripes - 1) * (stripe_spacing - stripe_height))
        start_y = (SCREEN_HEIGHT // 2) - (total_stripe_area // 2)
        
        # Draw white stripes (now horizontal across the road)
        for i in range(num_stripes):
            stripe_y = start_y + i * stripe_spacing
            stripe_rect = pygame.Rect(
                self.zebra_crossing_x - self.zebra_crossing_width // 2 + 10,
                stripe_y,
                self.zebra_crossing_width - 20,
                stripe_height
            )
            pygame.draw.rect(self.screen, WHITE, stripe_rect)
    
    def draw_traffic_light_labels(self):
        """Draw label for the pedestrian traffic light."""
        font = pygame.font.Font(None, 28)
        
        # Pedestrian traffic light label
        pedestrian_text = font.render("Pedestrian Crossing Light", True, BLACK)
        pedestrian_rect = pedestrian_text.get_rect(center=(
            self.pedestrian_light.x,
            self.pedestrian_light.y + 140  # Adjusted for side of road position
        ))
        self.screen.blit(pedestrian_text, pedestrian_rect)
    
    def draw_instructions(self):
        """Draw game instructions on screen."""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # Title
        title = font.render("Pedestrian Crossing Logic Gate Demo", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = small_font.render("Perfect for demonstrating AND, OR, XOR logic gates!", True, DARK_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "SPACE - Press pedestrian crossing button",
            "ESC - Exit game"
        ]
        
        y_offset = SCREEN_HEIGHT - 80
        for instruction in instructions:
            text = small_font.render(instruction, True, BLACK)
            self.screen.blit(text, (20, y_offset))
            y_offset += 25
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update game
            self.update(dt)
            
            # Draw everything
            self.draw()
        
        # Cleanup
        pygame.quit()
        sys.exit()

def main():
    """Main entry point."""
    game = TrafficLightGame()
    game.run()

if __name__ == "__main__":
    main()