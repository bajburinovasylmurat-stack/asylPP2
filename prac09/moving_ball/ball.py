import pygame

class Ball:

    def __init__(self, width, height):

        self.x = width // 2
        self.y = height // 2

        self.radius = 25

        self.width = width
        self.height = height

    def move(self, dx, dy):

        n_x = self.x + dx
        n_y = self.y + dy

        
        if n_x - self.radius >= 0 and n_x + self.radius <= self.width:
            self.x = n_x

        if n_y - self.radius >= 0 and n_y + self.radius <= self.height:
            self.y = n_y

    def draw(self, screen):

        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (self.x, self.y),
            self.radius
        )