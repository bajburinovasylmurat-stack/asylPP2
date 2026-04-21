import pygame
import datetime
import os
import math

class MickeyClock:

    def __init__(self, screen):
        self.screen = screen
        self.center = (900, 900)
        self.radius = 250

        current_path = os.path.dirname(__file__)
        image_path = os.path.join(current_path, "images", "mickey_hand.png")
        self.hand = pygame.image.load(image_path).convert_alpha()

        self.font = pygame.font.SysFont("Arial", 60, bold=True)

    def draw_face(self):
    
        pygame.draw.circle(self.screen, (220, 220, 220), self.center, self.radius)
        pygame.draw.circle(self.screen, (0, 0, 0), self.center, self.radius, 6)

        for i in range(1, 13):
            angle = math.radians(i * 30 - 90)
            x = self.center[0] + int((self.radius - 60) * math.cos(angle))
            y = self.center[1] + int((self.radius - 60) * math.sin(angle))
            text = self.font.render(str(i), True, (0, 0, 0))
            rect = text.get_rect(center=(x, y))
            self.screen.blit(text, rect)

        pygame.draw.circle(self.screen, (0, 0, 0), self.center, 12)

    def draw_hand(self, angle_deg):
        rotated = pygame.transform.rotate(self.hand, -angle_deg)
        rect = rotated.get_rect(center=self.center)
        self.screen.blit(rotated, rect)

    def draw(self):
        now = datetime.datetime.now()

        hour = now.hour % 12
        minute = now.minute
        second = now.second

        hour_angle   = hour * 30 + minute * 0.5   
        minute_angle = minute * 6
        second_angle = second * 6

        self.draw_face()                  
        self.draw_hand(hour_angle)          
        self.draw_hand(minute_angle)        
        self.draw_hand(second_angle)        