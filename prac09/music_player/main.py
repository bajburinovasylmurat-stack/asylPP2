import pygame
from player import MusicPlayer

pygame.init()

screen = pygame.display.set_mode((500, 300))
pygame.display.set_caption("Music Player")

clock = pygame.time.Clock()

player = MusicPlayer()

running = True

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_p:
                player.play()

            if event.key == pygame.K_s:
                player.stop()

            if event.key == pygame.K_n:
                player.next()

            if event.key == pygame.K_b:
                player.previous()

            if event.key == pygame.K_q:
                running = False

    player.draw(screen)

    pygame.display.update()
    clock.tick(30)

pygame.quit()