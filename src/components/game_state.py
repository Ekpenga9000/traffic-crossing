"""
Game State component for managing lives, score, and game over conditions
"""
import pygame
from ..utils.constants import *

class GameState:
    """
    Manages the game state including lives, score, and game over conditions.
    Players lose lives when pedestrians cross while the monster is visible.
    """
    
    def __init__(self):
        """
        Initialize the game state for single-chance gameplay.
        """
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.game_over_reason = None  # Track the reason for game over
        
        # Font for displaying text
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        # Tracking for collision detection
        self.pedestrians_crossed_safely = 0
        self.total_crossings_attempted = 0
        
        # Crossing guard state tracking for car collision detection
        self.previous_crossing_guard_state = None
        self.current_crossing_guard_state = None
        
        # Visual feedback
        self.life_lost_timer = 0  # Flash effect when life is lost
        self.life_lost_duration = 60  # 1 second at 60 FPS
    
    def lose_life(self, reason="Unknown"):
        """
        Trigger immediate game over (single-chance gameplay).
        
        Args:
            reason (str): Reason for game over (for debugging/feedback)
        """
        if not self.game_over:
            self.game_over = True
            self.game_over_reason = reason
            self.life_lost_timer = self.life_lost_duration
            print(f"Game Over! Reason: {reason}")
    
    def add_score(self, points):
        """
        Add points to the score.
        
        Args:
            points (int): Points to add
        """
        self.score += points
    
    def record_safe_crossing(self):
        """Record that a pedestrian crossed safely (monster not visible during crossing)."""
        self.pedestrians_crossed_safely += 1
        self.add_score(10)  # Award points for safe crossings
        print(f"Safe crossing! +10 points. Total safe crossings: {self.pedestrians_crossed_safely}, Score: {self.score}")
    
    def record_crossing_attempt(self):
        """Record that a crossing attempt was made."""
        self.total_crossings_attempted += 1
    
    def check_monster_pedestrian_collision(self, pedestrians, monster):
        """
        Check if any pedestrian is crossing while the monster is visible.
        
        Args:
            pedestrians (list): List of pedestrian objects
            monster: Monster object
            
        Returns:
            bool: True if collision detected (life should be lost)
        """
        # Only check if monster is visible (roaming state)
        if monster.state != 'roaming':
            return False
        
        # Check each pedestrian
        for pedestrian in pedestrians:
            # Check if pedestrian is actively crossing the road
            if pedestrian.state == 'crossing':
                # Pedestrian is crossing while monster is visible - danger!
                return True
        
        return False
    
    def check_car_collision(self, pedestrians, crossing_guard_state):
        """
        Check if crossing guard changed from 'walk' to 'stop' while pedestrians are crossing.
        This simulates a car collision when the signal changes unsafely.
        
        Args:
            pedestrians (list): List of pedestrian objects
            crossing_guard_state (str): Current crossing guard state ('walk' or 'stop')
            
        Returns:
            bool: True if dangerous signal change detected (life should be lost)
        """
        # Update crossing guard state tracking
        self.previous_crossing_guard_state = self.current_crossing_guard_state
        self.current_crossing_guard_state = crossing_guard_state
        
        # Check if signal just changed from 'walk' to 'stop'
        if (self.previous_crossing_guard_state == 'walk' and 
            self.current_crossing_guard_state == 'stop'):
            
            # Check if any pedestrians are still crossing when signal changed
            for pedestrian in pedestrians:
                if pedestrian.state == 'crossing':
                    # Dangerous! Pedestrian caught in crosswalk when signal changed to stop
                    return True
        
        return False
    
    def update(self, dt, pedestrians, monster, crossing_guard_state):
        """
        Update the game state, including collision detection and safe crossing tracking.
        
        Args:
            dt (float): Delta time since last frame
            pedestrians (list): List of pedestrian objects
            monster: Monster object
            crossing_guard_state (str): Current crossing guard state ('walk' or 'stop')
        """
        # Update visual feedback timers
        if self.life_lost_timer > 0:
            self.life_lost_timer -= 1
        
        # Check for car collision (signal changed dangerously)
        if self.check_car_collision(pedestrians, crossing_guard_state):
            # Find pedestrians caught in crossing when signal changed
            for pedestrian in pedestrians:
                if pedestrian.state == 'crossing' and not hasattr(pedestrian, 'car_collision_detected'):
                    pedestrian.car_collision_detected = True  # Mark to avoid multiple detections
                    self.lose_life("Crossing guard changed to STOP while pedestrian was crossing!")
                    break
        
        # Track pedestrians that are currently crossing
        for pedestrian in pedestrians:
            # Mark pedestrians when they start crossing for the first time
            if pedestrian.state == 'crossing' and not hasattr(pedestrian, 'crossing_tracked'):
                pedestrian.crossing_tracked = True
                pedestrian.monster_visible_during_crossing = (monster.state == 'roaming')
                self.record_crossing_attempt()
                
                # If monster is visible when they start crossing, lose a life immediately
                if pedestrian.monster_visible_during_crossing:
                    self.lose_life("Pedestrian crossed while monster was visible!")
            
            # Track pedestrians that finished crossing
            elif hasattr(pedestrian, 'crossing_tracked') and pedestrian.state == 'crossing_completed' and not hasattr(pedestrian, 'crossing_completed_processed'):
                pedestrian.crossing_completed_processed = True
                
                # If they completed crossing and monster was NOT visible during their crossing, it's a safe crossing
                if not pedestrian.monster_visible_during_crossing:
                    self.record_safe_crossing()
                    print(f"Safe crossing recorded! Total safe crossings: {self.pedestrians_crossed_safely}")
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.game_over_reason = None
        self.pedestrians_crossed_safely = 0
        self.total_crossings_attempted = 0
        self.life_lost_timer = 0
        # Reset crossing guard state tracking
        self.previous_crossing_guard_state = None
        self.current_crossing_guard_state = None
    
    def is_game_over(self):
        """Check if the game is over."""
        return self.game_over
    
    def get_score(self):
        """Get current score."""
        return self.score
    
    def draw(self, surface):
        """
        Draw the game state UI on the surface.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Draw score (moved up to replace lives position)
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, WHITE)
        surface.blit(score_surface, (10, 10))

        # Draw safe crossings counter (moved up)
        crossings_text = f"Safe Crossings: {self.pedestrians_crossed_safely}"
        crossings_surface = self.font.render(crossings_text, True, GREEN)
        surface.blit(crossings_surface, (10, 50))

        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            surface.blit(overlay, (0, 0))

            # Game over text
            game_over_text = "GAME OVER"
            game_over_surface = self.big_font.render(game_over_text, True, RED)
            game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            surface.blit(game_over_surface, game_over_rect)

            # Final score
            final_score_text = f"Final Score: {self.score}"
            score_surface = self.font.render(final_score_text, True, WHITE)
            score_rect = score_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
            surface.blit(score_surface, score_rect)

            # Restart instruction
            restart_text = "Press SPACE to restart or ESC to quit"
            restart_surface = self.font.render(restart_text, True, WHITE)
            restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            surface.blit(restart_surface, restart_rect)

        # Draw flashing warning when collision detected (different messages based on reason)
        if self.life_lost_timer > 0 and self.life_lost_timer % 10 < 5:  # Flash effect
            if self.game_over_reason and "crossing guard" in self.game_over_reason.lower():
                warning_text = "GAME OVER! Pedestrian was in flowing traffic."
            else:
                warning_text = "GAME OVER! The monster got the pedestrian."
            warning_surface = self.font.render(warning_text, True, RED)
            warning_rect = warning_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
            surface.blit(warning_surface, warning_rect)