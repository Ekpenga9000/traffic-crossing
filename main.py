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
from src.components.crossing_guard import CrossingGuard
from src.components.car import CarManager
from src.components.monster import MonsterManager
from src.components.pedestrian import PedestrianManager
from src.components.game_state import GameState

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
        
        # Single horizontal road (east-west) with zebra crossing - extends full viewport width
        self.road = Road(
            start_x=0, 
            start_y=center_y,
            end_x=SCREEN_WIDTH,
            end_y=center_y,
            num_lanes=2
        )
        
        # Zebra crossing position (center of the screen)
        self.zebra_crossing_x = center_x
        self.zebra_crossing_width = 100
        
        # Create traffic light
        self.traffic_lights = []
        
        # Crossing guard (replaces pedestrian traffic light) - positioned closer to the road
        self.crossing_guard = CrossingGuard(
            x=center_x + 80,                                  # Moved horizontally by 5rem (~80px)
            y=center_y - ROAD_WIDTH//2 - 60                   # Much closer to the road edge
        )
        self.crossing_guard.set_stop()  # Start with stop (pedestrians wait)
        self.traffic_lights.append(self.crossing_guard)  # Keep compatibility with existing code
        
        # Create car manager
        self.car_manager = CarManager(
            road_y=center_y,
            screen_width=SCREEN_WIDTH
        )
        
        # Create monster manager
        self.monster_manager = MonsterManager(
            road_y=center_y,
            screen_width=SCREEN_WIDTH,
            screen_height=SCREEN_HEIGHT
        )
        
        # Create pedestrian manager
        self.pedestrian_manager = PedestrianManager(
            road_y=center_y,
            screen_width=SCREEN_WIDTH,
            screen_height=SCREEN_HEIGHT,
            zebra_crossing_x=self.zebra_crossing_x,
            zebra_crossing_width=self.zebra_crossing_width
        )
        
        # Create game state manager
        self.game_state = GameState(initial_lives=3)
    
    def handle_events(self):
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.game_state.is_game_over():
                        # Restart game if game over
                        self.game_state.reset_game()
                        # Reset pedestrian and monster managers
                        self.pedestrian_manager = PedestrianManager(
                            road_y=self.road.start_y,
                            screen_width=SCREEN_WIDTH,
                            screen_height=SCREEN_HEIGHT,
                            zebra_crossing_x=self.zebra_crossing_x,
                            zebra_crossing_width=self.zebra_crossing_width
                        )
                    else:
                        # Toggle traffic lights when space is pressed
                        self.toggle_traffic_lights()
    
    def toggle_traffic_lights(self):
        """Toggle the crossing guard state."""
        # Simple toggle between stop and go for pedestrian crossing
        if self.crossing_guard.is_red():
            self.crossing_guard.set_green()  # Allow pedestrians to cross
        else:
            self.crossing_guard.set_red()     # Stop pedestrians
    
    def update(self, dt):
        """
        Update game state.
        
        Args:
            dt (float): Delta time since last frame
        """
        # Update traffic lights
        for light in self.traffic_lights:
            light.update(dt)
        
        # Update cars
        self.car_manager.update(dt, self.crossing_guard, self.zebra_crossing_x, self.zebra_crossing_width)
        
        # Update monsters with traffic light awareness
        self.monster_manager.update(dt, self.crossing_guard)
        
        # Update pedestrians with crossing guard state
        crossing_guard_state = 'walk' if self.crossing_guard.is_green() else 'stop'
        self.pedestrian_manager.update(dt, crossing_guard_state)
        
        # Update game state with collision detection
        if not self.game_state.is_game_over():
            pedestrians = self.pedestrian_manager.get_pedestrians()
            monster = self.monster_manager.get_monty()
            self.game_state.update(dt, pedestrians, monster, crossing_guard_state)
    
    def draw(self):
        """Draw the game."""
        # Clear screen with background color
        self.screen.fill(WHITE)
        
        # Draw the single road
        self.road.draw(self.screen)
        
        # Draw lane divider (center line)
        self.draw_lane_divider()
        
        # Draw zebra crossing
        self.draw_zebra_crossing()
        
                # Draw cars
        self.car_manager.draw(self.screen)
        
        # Draw monsters
        self.monster_manager.draw(self.screen)
        
        # Draw traffic lights (including crossing guard)
        for light in self.traffic_lights:
            light.draw(self.screen)
        
                # Draw pedestrians (render above crossing guard for proper z-index)
        self.pedestrian_manager.draw(self.screen)
        
        # Draw game state UI (lives, score, game over screen)
        self.game_state.draw(self.screen)
        
        # Draw labels for traffic lights
        self.draw_traffic_light_labels()
        
        # Draw instructions
        self.draw_instructions()
        
        # Update display
        pygame.display.flip()
    
    def draw_lane_divider(self):
        """Draw the center lane divider for two-way traffic."""
        center_y = SCREEN_HEIGHT // 2
        line_width = 3
        
        # Draw solid center line across the entire road
        # Left segment (before zebra crossing)
        left_end = self.zebra_crossing_x - self.zebra_crossing_width//2
        if left_end > 50:
            pygame.draw.rect(self.screen, YELLOW, 
                           (50, center_y - line_width//2, left_end - 50, line_width))
        
        # Right segment (after zebra crossing)  
        right_start = self.zebra_crossing_x + self.zebra_crossing_width//2
        if right_start < SCREEN_WIDTH - 50:
            pygame.draw.rect(self.screen, YELLOW,
                           (right_start, center_y - line_width//2, 
                            SCREEN_WIDTH - 50 - right_start, line_width))
    
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
        """Draw label for the crossing guard."""
        font = pygame.font.Font(None, 28)
        
        # Crossing guard label - positioned to the right side
        guard_text = font.render("Crossing Guard", True, BLACK)
        guard_rect = guard_text.get_rect(midleft=(
            self.crossing_guard.x + 60,  # To the right of the crossing guard
            self.crossing_guard.y        # Vertically centered with the crossing guard
        ))
        self.screen.blit(guard_text, guard_rect)
    
    def draw_instructions(self):
        """Draw game instructions on screen."""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # Title
        title = font.render("Crossing Guard Logic Gate Demo", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = small_font.render("Perfect for demonstrating AND, OR, XOR logic gates!", True, DARK_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "SPACE - Signal crossing guard to change",
            f"Cars on road: {self.car_manager.get_car_count()}",
            "ESC - Exit game"
        ]
        
        y_offset = SCREEN_HEIGHT - 100
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