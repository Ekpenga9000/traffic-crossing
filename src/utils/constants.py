"""
Constants for the Traffic Light Logic Gate Game
"""

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (200, 200, 200)

# Traffic light colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
TRAFFIC_LIGHT_OFF = (50, 50, 50)

# Road colors
ROAD_COLOR = DARK_GRAY
LANE_MARKER_COLOR = YELLOW
SIDEWALK_COLOR = LIGHT_GRAY

# Additional colors for car details
LIGHT_BLUE = (150, 200, 255)
DARK_BLUE = (0, 0, 139)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Traffic light dimensions (for 2-light pedestrian crossing)
LIGHT_RADIUS = 20
LIGHT_BOX_WIDTH = 50
LIGHT_BOX_HEIGHT = 120  # Reduced height for 2 lights only (red and green)
LIGHT_POLE_WIDTH = 8
LIGHT_POLE_HEIGHT = 100

# Road dimensions
ROAD_WIDTH = 200
LANE_WIDTH = 100
LANE_MARKER_WIDTH = 4
LANE_MARKER_LENGTH = 30
LANE_MARKER_GAP = 20

# Intersection dimensions
INTERSECTION_SIZE = 300