import pygame
import random

pygame.init()

w = 600
h = 400
cell = 20

screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

snake = [(100, 100), (80, 100), (60, 100)]
dx = cell
dy = 0

food = (0, 0)

def new_food():
    while True:
        x = random.randrange(0, w, cell)
        y = random.randrange(0, h, cell)
        if (x, y) not in snake:
            return (x, y)

food = new_food()

score = 0
level = 1
speed = 7

running = True

while running:

    clock.tick(speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_UP and dy == 0:
                dx = 0
                dy = -cell

            if event.key == pygame.K_DOWN and dy == 0:
                dx = 0
                dy = cell

            if event.key == pygame.K_LEFT and dx == 0:
                dx = -cell
                dy = 0

            if event.key == pygame.K_RIGHT and dx == 0:
                dx = cell
                dy = 0

    head_x, head_y = snake[0]
    new_head = (head_x + dx, head_y + dy)

    if new_head[0] < 0 or new_head[0] >= w or new_head[1] < 0 or new_head[1] >= h:
        running = False

    if new_head in snake:
        running = False

    snake.insert(0, new_head)

    if new_head == food:
        score += 1
        food = new_food()

        if score % 3 == 0:
            level += 1
            speed += 2
    else:
        snake.pop()

    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, (255, 0, 0), (*food, cell, cell))

    for i in snake:
        pygame.draw.rect(screen, (0, 255, 0), (*i, cell, cell))

    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Score: {score} Level: {level}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.update()

pygame.quit()