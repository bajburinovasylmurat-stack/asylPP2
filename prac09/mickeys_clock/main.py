import pygame
from clock import MickeyClock

pygame.init()

# Терезе өлшемі
W = 1600
H = 1600

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Mickey Clock")

clock = pygame.time.Clock()

mickey_clock = MickeyClock(screen)

running = True

while running:
    screen.fill((255, 255, 255))  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mickey_clock.draw()

    pygame.display.update()
    clock.tick(1)  # әр секунд сайын жаңарады

pygame.quit()