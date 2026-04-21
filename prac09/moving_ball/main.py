import pygame
from ball import Ball

pygame.init()

W = 600
H = 400

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Moving Ball")

clock = pygame.time.Clock()

ball = Ball(W, H)

running = True

while running:

    screen.fill((255, 255, 255))

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP:
                ball.move(0, -20)

            if event.key == pygame.K_DOWN:
                ball.move(0, 20)

            if event.key == pygame.K_LEFT:
                ball.move(-20, 0)

            if event.key == pygame.K_RIGHT:
                ball.move(20, 0)

    ball.draw(screen)

    pygame.display.update()
    clock.tick(30)

pygame.quit()