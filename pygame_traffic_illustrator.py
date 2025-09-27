import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Try to initialize audio mixer, but don't fail if it's not available
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error:
    AUDIO_AVAILABLE = False
    print("Audio not available - running in silent mode")

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
INPUT_PANEL_WIDTH = 300
INTERSECTION_PANEL_WIDTH = 600
TRUTH_TABLE_HEIGHT = 200

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
LED_ON = (0, 255, 0)
LED_OFF = (50, 50, 50)
SWITCH_ON = (100, 255, 100)
SWITCH_OFF = (255, 100, 100)
PANEL_BG = (240, 240, 240)

# Display setup
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Logic Gate Traffic Light Educational Game")
clock = pygame.time.Clock()

# Sound system
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = AUDIO_AVAILABLE
        if self.enabled:
            self.create_placeholder_sounds()
    
    def create_placeholder_sounds(self):
        """Create simple tone sounds as placeholders"""
        try:
            # Create simple empty sounds as placeholders
            # In a real implementation, you would load actual sound files
            self.sounds['click'] = None
            self.sounds['complete'] = None
        except:
            # If sound creation fails, disable sounds
            self.enabled = False
    
    def play(self, sound_name):
        # For now, just print to console since we don't have actual sound files
        if self.enabled and sound_name in self.sounds:
            pass  # Would play actual sound file here

sound_manager = SoundManager()

class Node:
    """Represents a boolean input or output in the logic system"""
    def __init__(self, initial_value=False):
        self.value = initial_value
        self.observers = []  # Gates or components that depend on this node
    
    def set_value(self, value):
        if self.value != value:
            self.value = value
            self.notify_observers()
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify_observers(self):
        for observer in self.observers:
            observer.update()

class Gate:
    """Logic gate that supports AND, OR, XOR operations"""
    def __init__(self, gate_type, input_a, input_b):
        self.gate_type = gate_type.upper()
        self.input_a = input_a
        self.input_b = input_b
        self.output = Node()
        
        # Register as observer of inputs
        self.input_a.add_observer(self)
        self.input_b.add_observer(self)
        
        self.update()  # Initial calculation
    
    def update(self):
        """Calculate output based on gate type and inputs"""
        a = self.input_a.value
        b = self.input_b.value
        
        if self.gate_type == "AND":
            result = a and b
        elif self.gate_type == "OR":
            result = a or b
        elif self.gate_type == "XOR":
            result = a != b  # XOR: true when inputs are different
        else:
            result = False
        
        self.output.set_value(result)

class TrafficLight:
    """Traffic light that responds to gate output with smooth animations"""
    def __init__(self, x, y, gate_output):
        self.x = x
        self.y = y
        self.gate_output = gate_output
        self.is_green = False
        self.transition_alpha = 0.0  # For smooth color transitions
        self.target_alpha = 0.0
        self.light_radius = 20
        
        # Register as observer of gate output
        self.gate_output.add_observer(self)
    
    def update(self):
        """Update light state based on gate output"""
        target_green = self.gate_output.value
        if target_green != self.is_green:
            self.is_green = target_green
            self.target_alpha = 1.0 if target_green else 0.0
    
    def animate(self):
        """Smooth transition animation"""
        if abs(self.transition_alpha - self.target_alpha) > 0.01:
            self.transition_alpha += (self.target_alpha - self.transition_alpha) * 0.1
        else:
            self.transition_alpha = self.target_alpha
    
    def draw(self, surface):
        # Traffic light box
        box_rect = pygame.Rect(self.x - 25, self.y - 60, 50, 80)
        pygame.draw.rect(surface, DARK_GRAY, box_rect)
        pygame.draw.rect(surface, BLACK, box_rect, 2)
        
        # Red light (top)
        red_intensity = int(255 * (1.0 - self.transition_alpha))
        red_color = (red_intensity, 0, 0) if red_intensity > 50 else (50, 0, 0)
        pygame.draw.circle(surface, red_color, (self.x, self.y - 25), self.light_radius)
        
        # Green light (bottom)
        green_intensity = int(255 * self.transition_alpha)
        green_color = (0, green_intensity, 0) if green_intensity > 50 else (0, 50, 0)
        pygame.draw.circle(surface, green_color, (self.x, self.y + 5), self.light_radius)
        
        # LED output indicator
        led_color = LED_ON if self.is_green else LED_OFF
        pygame.draw.circle(surface, led_color, (self.x + 40, self.y - 10), 8)
        pygame.draw.circle(surface, BLACK, (self.x + 40, self.y - 10), 8, 2)

class InputSwitch:
    """Interactive input switch with LED indicator"""
    def __init__(self, x, y, width, height, label, node):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.node = node
        self.font = pygame.font.Font(None, 28)
        self.led_pos = (x + width + 20, y + height // 2)
    
    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.node.set_value(not self.node.value)
            sound_manager.play('click')
            return True
        return False
    
    def handle_key(self, key):
        """Handle keyboard input"""
        if (self.label == "Input A" and key == pygame.K_a) or \
           (self.label == "Input B" and key == pygame.K_b):
            self.node.set_value(not self.node.value)
            sound_manager.play('click')
            return True
        return False
    
    def draw(self, surface):
        # Switch button
        color = SWITCH_ON if self.node.value else SWITCH_OFF
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 3, border_radius=10)
        
        # Switch text
        state_text = "ON" if self.node.value else "OFF"
        text = self.font.render(state_text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
        # Label
        label_text = self.font.render(self.label, True, BLACK)
        surface.blit(label_text, (self.rect.x, self.rect.y - 30))
        
        # LED indicator
        led_color = LED_ON if self.node.value else LED_OFF
        pygame.draw.circle(surface, led_color, self.led_pos, 12)
        pygame.draw.circle(surface, BLACK, self.led_pos, 12, 2)

class TruthTableLogger:
    """Tracks and displays the live truth table"""
    def __init__(self, x, y, input_a, input_b, gates):
        self.x = x
        self.y = y
        self.input_a = input_a
        self.input_b = input_b
        self.gates = gates  # Dictionary of gate_name: gate
        self.history = set()  # Track which combinations have been tried
        self.font = pygame.font.Font(None, 24)
        self.header_font = pygame.font.Font(None, 28)
        
        # Register as observer
        input_a.add_observer(self)
        input_b.add_observer(self)
    
    def update(self):
        """Log current input combination"""
        combo = (self.input_a.value, self.input_b.value)
        self.history.add(combo)
    
    def draw(self, surface):
        # Panel background
        panel_rect = pygame.Rect(self.x - 10, self.y - 10, WINDOW_WIDTH - self.x + 10, TRUTH_TABLE_HEIGHT + 20)
        pygame.draw.rect(surface, PANEL_BG, panel_rect)
        pygame.draw.rect(surface, BLACK, panel_rect, 2)
        
        # Title
        title = self.header_font.render("Live Truth Table", True, BLACK)
        surface.blit(title, (self.x, self.y))
        
        # Headers
        headers = ["A", "B", "AND", "OR", "XOR"]
        header_y = self.y + 40
        col_width = 80
        
        for i, header in enumerate(headers):
            text = self.header_font.render(header, True, BLACK)
            header_rect = text.get_rect(center=(self.x + i * col_width + 40, header_y))
            surface.blit(text, header_rect)
        
        # Draw header underline
        pygame.draw.line(surface, BLACK, 
                        (self.x, header_y + 20), 
                        (self.x + len(headers) * col_width, header_y + 20), 2)
        
        # Truth table rows
        row_y = header_y + 35
        combinations = [(False, False), (False, True), (True, False), (True, True)]
        
        for a_val, b_val in combinations:
            combo = (a_val, b_val)
            
            # Highlight current combination
            if (self.input_a.value, self.input_b.value) == combo:
                highlight_rect = pygame.Rect(self.x - 5, row_y - 5, len(headers) * col_width + 10, 25)
                pygame.draw.rect(surface, YELLOW, highlight_rect, border_radius=5)
            
            # Show values if combination has been tried
            if combo in self.history:
                values = [
                    str(int(a_val)), 
                    str(int(b_val)),
                    str(int(self.gates["AND"].output.value if (a_val, b_val) == (self.input_a.value, self.input_b.value) else (a_val and b_val))),
                    str(int(self.gates["OR"].output.value if (a_val, b_val) == (self.input_a.value, self.input_b.value) else (a_val or b_val))),
                    str(int(self.gates["XOR"].output.value if (a_val, b_val) == (self.input_a.value, self.input_b.value) else (a_val != b_val)))
                ]
                
                for i, value in enumerate(values):
                    text = self.font.render(value, True, BLACK)
                    text_rect = text.get_rect(center=(self.x + i * col_width + 40, row_y + 10))
                    surface.blit(text, text_rect)
            else:
                # Show question marks for untried combinations
                for i in range(len(headers)):
                    if i < 2:  # Always show A and B values
                        value = str(int(a_val)) if i == 0 else str(int(b_val))
                        text = self.font.render(value, True, GRAY)
                    else:
                        text = self.font.render("?", True, GRAY)
                    text_rect = text.get_rect(center=(self.x + i * col_width + 40, row_y + 10))
                    surface.blit(text, text_rect)
            
            row_y += 30
        
        # Progress indicator
        progress_text = f"Combinations tried: {len(self.history)}/4"
        progress = self.font.render(progress_text, True, BLACK)
        surface.blit(progress, (self.x, self.y + 165))

class GameScene:
    """Main game manager handling different modes"""
    def __init__(self):
        # Create input nodes
        self.input_a = Node(False)
        self.input_b = Node(False)
        
        # Create logic gates
        self.gates = {
            "AND": Gate("AND", self.input_a, self.input_b),
            "OR": Gate("OR", self.input_a, self.input_b),
            "XOR": Gate("XOR", self.input_a, self.input_b)
        }
        
        # Create UI components
        self.input_switches = [
            InputSwitch(50, 100, 120, 50, "Input A", self.input_a),
            InputSwitch(50, 200, 120, 50, "Input B", self.input_b)
        ]
        
        # Create traffic lights
        intersection_start_x = INPUT_PANEL_WIDTH + 100
        intersection_spacing = 180
        intersection_y = 200
        
        self.traffic_lights = [
            TrafficLight(intersection_start_x, intersection_y, self.gates["AND"].output),
            TrafficLight(intersection_start_x + intersection_spacing, intersection_y, self.gates["OR"].output),
            TrafficLight(intersection_start_x + intersection_spacing * 2, intersection_y, self.gates["XOR"].output)
        ]
        
        # Create truth table logger
        self.truth_table = TruthTableLogger(50, WINDOW_HEIGHT - TRUTH_TABLE_HEIGHT, 
                                          self.input_a, self.input_b, self.gates)
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 48)
        
        # Game state
        self.mode = "MENU"  # MENU, FREE_PLAY, TUTORIAL, CHALLENGE
        self.tutorial_level = 1
        self.score = 0
        self.tutorial_completed = False
        
        # Tutorial scenarios
        self.tutorial_scenarios = [
            {
                "title": "Level 1: Learn the Basics",
                "description": "Try all 4 input combinations (00, 01, 10, 11) to complete the truth table",
                "goal": "Complete all truth table entries",
                "check_completion": lambda: len(self.truth_table.history) >= 4
            },
            {
                "title": "Level 2: Emergency Vehicles", 
                "description": "Input A = Normal Traffic, Input B = Emergency Vehicle. Which gate allows emergency vehicles to always pass?",
                "goal": "Find which gate gives green light when emergency vehicle (B=1) is present",
                "check_completion": lambda: self.input_b.value and any(gate.output.value for gate in self.gates.values())
            },
            {
                "title": "Level 3: Exclusive Access",
                "description": "Input A = VIP Car, Input B = Regular Car. Only one type should pass at a time.",
                "goal": "Find which gate allows exactly one input to cause green light",
                "check_completion": lambda: self.gates["XOR"].output.value and (self.input_a.value != self.input_b.value)
            }
        ]
        
        self.current_scenario = 0
        
        # Initialize truth table
        self.truth_table.update()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.mode != "MENU":
                        self.mode = "MENU"
                    else:
                        return False
                elif self.mode == "MENU":
                    if event.key == pygame.K_1:
                        self.mode = "FREE_PLAY"
                    elif event.key == pygame.K_2:
                        self.mode = "TUTORIAL"
                        self.current_scenario = 0
                        self.reset_game_state()
                    elif event.key == pygame.K_q:
                        return False
                elif self.mode == "TUTORIAL":
                    if event.key == pygame.K_n:  # Next level
                        if self.current_scenario < len(self.tutorial_scenarios) - 1:
                            self.current_scenario += 1
                            self.reset_game_state()
                    elif event.key == pygame.K_r:  # Reset current level
                        self.reset_game_state()
                    else:
                        # Handle input switches
                        for switch in self.input_switches:
                            if switch.handle_key(event.key):
                                self.check_tutorial_completion()
                else:  # FREE_PLAY or other modes
                    # Handle input switches
                    for switch in self.input_switches:
                        switch.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.mode in ["FREE_PLAY", "TUTORIAL"]:
                    # Handle switch clicks
                    for switch in self.input_switches:
                        if switch.handle_click(event.pos):
                            # Check tutorial completion after input change
                            if self.mode == "TUTORIAL":
                                self.check_tutorial_completion()
        return True
    
    def check_tutorial_completion(self):
        """Check if current tutorial level is completed"""
        scenario = self.tutorial_scenarios[self.current_scenario]
        if scenario["check_completion"]():
            sound_manager.play('complete')
    
    def reset_game_state(self):
        """Reset inputs and truth table for new level"""
        self.input_a.set_value(False)
        self.input_b.set_value(False)
        self.truth_table.history.clear()
        self.truth_table.update()
    
    def update(self):
        # Animate traffic lights
        for light in self.traffic_lights:
            light.animate()
    
    def draw_panels(self, surface):
        # Input panel background
        input_panel = pygame.Rect(0, 0, INPUT_PANEL_WIDTH, WINDOW_HEIGHT - TRUTH_TABLE_HEIGHT)
        pygame.draw.rect(surface, PANEL_BG, input_panel)
        pygame.draw.rect(surface, BLACK, input_panel, 3)
        
        # Intersection panel background  
        intersection_panel = pygame.Rect(INPUT_PANEL_WIDTH, 0, INTERSECTION_PANEL_WIDTH, WINDOW_HEIGHT - TRUTH_TABLE_HEIGHT)
        pygame.draw.rect(surface, WHITE, intersection_panel)
        pygame.draw.rect(surface, BLACK, intersection_panel, 3)
    
    def draw_intersections(self, surface):
        # Draw roads and intersections
        gate_names = ["AND", "OR", "XOR"]
        
        for i, (light, gate_name) in enumerate(zip(self.traffic_lights, gate_names)):
            # Draw intersection roads
            # Horizontal road
            road_rect = pygame.Rect(INPUT_PANEL_WIDTH, light.y - 15, INTERSECTION_PANEL_WIDTH, 30)
            pygame.draw.rect(surface, DARK_GRAY, road_rect)
            
            # Vertical road
            road_rect = pygame.Rect(light.x - 15, 0, 30, WINDOW_HEIGHT - TRUTH_TABLE_HEIGHT)
            pygame.draw.rect(surface, DARK_GRAY, road_rect)
            
            # Lane markings
            for x in range(INPUT_PANEL_WIDTH + 20, INPUT_PANEL_WIDTH + INTERSECTION_PANEL_WIDTH, 40):
                pygame.draw.rect(surface, YELLOW, (x, light.y - 2, 20, 4))
            
            # Draw traffic light
            light.draw(surface)
            
            # Gate label
            label = self.title_font.render(f"{gate_name} Intersection", True, BLACK)
            label_rect = label.get_rect(center=(light.x, light.y + 100))
            surface.blit(label, label_rect)
            
            # Gate explanation
            explanations = {
                "AND": "Green when BOTH inputs are true",
                "OR": "Green when AT LEAST ONE input is true", 
                "XOR": "Green when EXACTLY ONE input is true"
            }
            
            explanation = self.font.render(explanations[gate_name], True, DARK_GRAY)
            exp_rect = explanation.get_rect(center=(light.x, light.y + 130))
            surface.blit(explanation, exp_rect)
    
    def draw_instructions(self, surface):
        instructions = [
            "CONTROLS:",
            "• Press 'A' or click to toggle Input A",
            "• Press 'B' or click to toggle Input B", 
            "• ESC to quit",
            "",
            "GOAL:",
            "Try all 4 input combinations",
            "and observe the differences",
            "between AND, OR, and XOR gates!"
        ]
        
        start_y = 300
        for instruction in instructions:
            if instruction.startswith("CONTROLS:") or instruction.startswith("GOAL:"):
                text = self.font.render(instruction, True, BLACK)
            else:
                text = self.small_font.render(instruction, True, DARK_GRAY)
            surface.blit(text, (20, start_y))
            start_y += 25
    
    def draw(self, surface):
        surface.fill(WHITE)
        
        if self.mode == "MENU":
            self.draw_menu(surface)
        elif self.mode == "TUTORIAL":
            self.draw_tutorial_mode(surface)
        else:  # FREE_PLAY
            self.draw_free_play_mode(surface)
    
    def draw_menu(self, surface):
        """Draw the main menu screen"""
        # Title
        title = self.large_font.render("Logic Gate Traffic Simulator", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        surface.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.title_font.render("Educational Game", True, DARK_GRAY)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 200))
        surface.blit(subtitle, subtitle_rect)
        
        # Menu options
        menu_items = [
            "1. Free Play Mode - Explore logic gates freely",
            "2. Tutorial Mode - Learn with guided lessons", 
            "Q. Quit Game"
        ]
        
        start_y = 300
        for item in menu_items:
            text = self.font.render(item, True, BLACK)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, start_y))
            surface.blit(text, text_rect)
            start_y += 50
        
        # Instructions
        instruction = self.font.render("Press the corresponding key to select", True, DARK_GRAY)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, start_y + 50))
        surface.blit(instruction, instruction_rect)
    
    def draw_tutorial_mode(self, surface):
        """Draw the tutorial mode interface"""
        # Draw panel backgrounds
        self.draw_panels(surface)
        
        # Tutorial header
        scenario = self.tutorial_scenarios[self.current_scenario]
        title = self.title_font.render(scenario["title"], True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        surface.blit(title, title_rect)
        
        # Draw input switches
        for switch in self.input_switches:
            switch.draw(surface)
        
        # Draw intersections and traffic lights
        self.draw_intersections(surface)
        
        # Draw tutorial instructions
        self.draw_tutorial_instructions(surface)
        
        # Draw truth table
        self.truth_table.draw(surface)
        
        # Check completion
        if scenario["check_completion"]():
            self.draw_completion_message(surface)
    
    def draw_free_play_mode(self, surface):
        """Draw the free play mode interface"""
        # Draw panel backgrounds
        self.draw_panels(surface)
        
        # Draw title
        title = self.title_font.render("Logic Gate Traffic Simulator - Free Play", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        surface.blit(title, title_rect)
        
        # Draw input switches
        for switch in self.input_switches:
            switch.draw(surface)
        
        # Draw intersections and traffic lights
        self.draw_intersections(surface)
        
        # Draw instructions
        self.draw_instructions(surface)
        
        # Draw truth table
        self.truth_table.draw(surface)
    
    def draw_tutorial_instructions(self, surface):
        """Draw tutorial-specific instructions"""
        scenario = self.tutorial_scenarios[self.current_scenario]
        
        instructions = [
            "TUTORIAL CONTROLS:",
            "• Press 'A' or click to toggle Input A",
            "• Press 'B' or click to toggle Input B",
            "• Press 'N' for next level",
            "• Press 'R' to reset level",
            "• ESC to return to menu",
            "",
            "SCENARIO:",
            scenario["description"],
            "",
            "GOAL:",
            scenario["goal"]
        ]
        
        start_y = 300
        for instruction in instructions:
            if instruction.startswith("TUTORIAL") or instruction.startswith("SCENARIO:") or instruction.startswith("GOAL:"):
                text = self.font.render(instruction, True, BLACK)
            else:
                text = self.small_font.render(instruction, True, DARK_GRAY)
            surface.blit(text, (20, start_y))
            start_y += 25
    
    def draw_completion_message(self, surface):
        """Draw completion message when tutorial level is finished"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Completion message
        completion_text = self.title_font.render("Level Complete!", True, GREEN)
        completion_rect = completion_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        surface.blit(completion_text, completion_rect)
        
        if self.current_scenario < len(self.tutorial_scenarios) - 1:
            next_text = self.font.render("Press 'N' for next level", True, WHITE)
            next_rect = next_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            surface.blit(next_text, next_rect)
        else:
            final_text = self.font.render("Tutorial Complete! Press ESC for menu", True, WHITE)
            final_rect = final_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            surface.blit(final_text, final_rect)

def main():
    game = GameScene()
    
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()