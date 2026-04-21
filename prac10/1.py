import pygame
import random

pygame.init()

WIDTH = 500
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Game")

clock = pygame.time.Clock()


car_width = 50
car_height = 80
car_x = WIDTH // 2
car_y = HEIGHT - 100
car_speed = 5

car_rect = pygame.Rect(car_x, car_y, car_width, car_height)

coin_radius = 15
coin_x = random.randint(50, WIDTH - 50)
coin_y = random.randint(-600, -50)
coin_speed = 5

score = 0
font = pygame.font.SysFont("Arial", 28)


running = True

while running:
    clock.tick(60) 

    screen.fill((30, 30, 30))  


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and car_x > 0:
        car_x -= car_speed
    if keys[pygame.K_RIGHT] and car_x < WIDTH - car_width:
        car_x += car_speed

    car_rect.x = car_x
    car_rect.y = car_y


    coin_y += coin_speed

    if coin_y > HEIGHT:
        coin_y = random.randint(-600, -50)
        coin_x = random.randint(50, WIDTH - 50)

    coin_rect = pygame.Rect(
        coin_x - coin_radius,
        coin_y - coin_radius,
        coin_radius * 2,
        coin_radius * 2
    )

    if car_rect.colliderect(coin_rect):
        score += 1  

        coin_y = random.randint(-600, -50)
        coin_x = random.randint(50, WIDTH - 50)

    
    pygame.draw.rect(screen, (0, 200, 255), car_rect)

  
    pygame.draw.circle(screen, (255, 215, 0), (coin_x, coin_y), coin_radius)

    score_text = font.render(f"Coins: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.update()

pygame.quit()