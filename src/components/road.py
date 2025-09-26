"""
Road component for the traffic light game
"""
import pygame
import math
from ..utils.constants import *

class Road:
    """
    A road segment that can be horizontal or vertical, with lanes and markings.
    """
    
    def __init__(self, start_x, start_y, end_x, end_y, num_lanes=2):
        """
        Initialize a road segment.
        
        Args:
            start_x (int): Starting X coordinate
            start_y (int): Starting Y coordinate
            end_x (int): Ending X coordinate
            end_y (int): Ending Y coordinate
            num_lanes (int): Number of lanes (default 2 for bidirectional)
        """
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.num_lanes = num_lanes
        
        # Calculate road properties
        self.length = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        self.angle = math.atan2(end_y - start_y, end_x - start_x)
        
        # Determine if road is primarily horizontal or vertical
        angle_degrees = math.degrees(self.angle) % 360
        self.is_horizontal = abs(angle_degrees) < 45 or abs(angle_degrees - 180) < 45
        
        # Calculate road width based on number of lanes
        self.road_width = num_lanes * LANE_WIDTH
        
        # Calculate road rectangle
        if self.is_horizontal:
            # Horizontal road
            self.road_rect = pygame.Rect(
                min(start_x, end_x),
                min(start_y, end_y) - self.road_width // 2,
                abs(end_x - start_x),
                self.road_width
            )
        else:
            # Vertical road
            self.road_rect = pygame.Rect(
                min(start_x, end_x) - self.road_width // 2,
                min(start_y, end_y),
                self.road_width,
                abs(end_y - start_y)
            )
    
    def draw(self, surface):
        """
        Draw the road on the surface.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Draw main road surface
        pygame.draw.rect(surface, ROAD_COLOR, self.road_rect)
        pygame.draw.rect(surface, BLACK, self.road_rect, 2)
        
        # Draw lane markings
        self._draw_lane_markings(surface)
        
        # Draw road edges
        self._draw_road_edges(surface)
    
    def _draw_lane_markings(self, surface):
        """Draw dashed lane markings down the center of the road."""
        if self.num_lanes < 2:
            return
            
        if self.is_horizontal:
            # Horizontal road - vertical lane markings
            center_y = self.road_rect.centery
            marking_x = self.road_rect.left
            
            while marking_x < self.road_rect.right:
                # Draw dashed line segment
                marking_rect = pygame.Rect(
                    marking_x,
                    center_y - LANE_MARKER_WIDTH // 2,
                    LANE_MARKER_LENGTH,
                    LANE_MARKER_WIDTH
                )
                pygame.draw.rect(surface, LANE_MARKER_COLOR, marking_rect)
                marking_x += LANE_MARKER_LENGTH + LANE_MARKER_GAP
        else:
            # Vertical road - horizontal lane markings  
            center_x = self.road_rect.centerx
            marking_y = self.road_rect.top
            
            while marking_y < self.road_rect.bottom:
                # Draw dashed line segment
                marking_rect = pygame.Rect(
                    center_x - LANE_MARKER_WIDTH // 2,
                    marking_y,
                    LANE_MARKER_WIDTH,
                    LANE_MARKER_LENGTH
                )
                pygame.draw.rect(surface, LANE_MARKER_COLOR, marking_rect)
                marking_y += LANE_MARKER_LENGTH + LANE_MARKER_GAP
    
    def _draw_road_edges(self, surface):
        """Draw solid lines at the edges of the road."""
        edge_width = 3
        
        if self.is_horizontal:
            # Top edge
            pygame.draw.line(surface, WHITE, 
                           (self.road_rect.left, self.road_rect.top),
                           (self.road_rect.right, self.road_rect.top), edge_width)
            # Bottom edge
            pygame.draw.line(surface, WHITE,
                           (self.road_rect.left, self.road_rect.bottom),
                           (self.road_rect.right, self.road_rect.bottom), edge_width)
        else:
            # Left edge
            pygame.draw.line(surface, WHITE,
                           (self.road_rect.left, self.road_rect.top),
                           (self.road_rect.left, self.road_rect.bottom), edge_width)
            # Right edge
            pygame.draw.line(surface, WHITE,
                           (self.road_rect.right, self.road_rect.top),
                           (self.road_rect.right, self.road_rect.bottom), edge_width)
    
    def get_center_point(self):
        """Get the center point of the road."""
        return (self.road_rect.centerx, self.road_rect.centery)
    
    def get_lane_positions(self):
        """Get the center positions of each lane."""
        positions = []
        
        if self.is_horizontal:
            # For horizontal roads, lanes are stacked vertically
            lane_height = self.road_width // self.num_lanes
            for i in range(self.num_lanes):
                lane_y = self.road_rect.top + (i + 0.5) * lane_height
                positions.append({
                    'center_y': lane_y,
                    'left_x': self.road_rect.left,
                    'right_x': self.road_rect.right
                })
        else:
            # For vertical roads, lanes are side by side
            lane_width = self.road_width // self.num_lanes
            for i in range(self.num_lanes):
                lane_x = self.road_rect.left + (i + 0.5) * lane_width
                positions.append({
                    'center_x': lane_x,
                    'top_y': self.road_rect.top,
                    'bottom_y': self.road_rect.bottom
                })
        
        return positions

class Intersection:
    """
    An intersection where roads meet, controlled by traffic lights.
    """
    
    def __init__(self, x, y, size=INTERSECTION_SIZE):
        """
        Initialize an intersection.
        
        Args:
            x (int): Center X coordinate
            y (int): Center Y coordinate
            size (int): Size of the intersection square
        """
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        
        # Roads connected to this intersection
        self.roads = []
        self.traffic_lights = []
    
    def add_road(self, road):
        """Add a road that connects to this intersection."""
        self.roads.append(road)
    
    def add_traffic_light(self, traffic_light):
        """Add a traffic light to this intersection."""
        self.traffic_lights.append(traffic_light)
    
    def draw(self, surface):
        """
        Draw the intersection.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Draw intersection surface
        pygame.draw.rect(surface, ROAD_COLOR, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 3)
        
        # Draw crosswalk markings
        self._draw_crosswalk_markings(surface)
    
    def _draw_crosswalk_markings(self, surface):
        """Draw crosswalk markings across the intersection."""
        stripe_width = 8
        stripe_spacing = 12
        
        # Horizontal crosswalks (top and bottom)
        for side in ['top', 'bottom']:
            y_pos = self.rect.top if side == 'top' else self.rect.bottom - stripe_width
            
            for x in range(self.rect.left, self.rect.right, stripe_spacing):
                stripe_rect = pygame.Rect(x, y_pos, stripe_width, stripe_width)
                if stripe_rect.right <= self.rect.right:
                    pygame.draw.rect(surface, WHITE, stripe_rect)
        
        # Vertical crosswalks (left and right)
        for side in ['left', 'right']:
            x_pos = self.rect.left if side == 'left' else self.rect.right - stripe_width
            
            for y in range(self.rect.top, self.rect.bottom, stripe_spacing):
                stripe_rect = pygame.Rect(x_pos, y, stripe_width, stripe_width)
                if stripe_rect.bottom <= self.rect.bottom:
                    pygame.draw.rect(surface, WHITE, stripe_rect)