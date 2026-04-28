import pygame
from persistence import load_settings, save_settings, add_score
from ui import (
    UsernameScreen, MainMenu, SettingsScreen,
    LeaderboardScreen, GameOverScreen,
)
from racer import GameSession, WIDTH, HEIGHT

FPS = 60


def main():
    pygame.init()
    screen  = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Turbo Racer — TSIS 3")
    clock   = pygame.time.Clock()

    settings = load_settings()

    if not settings.get("username", "").strip():
        state = "username"
    else:
        state = "menu"

    current_screen = None

    def build(s):
        nonlocal current_screen
        if s == "username":
            current_screen = UsernameScreen(WIDTH, HEIGHT, settings)
        elif s == "menu":
            current_screen = MainMenu(WIDTH, HEIGHT, settings)
        elif s == "settings":
            current_screen = SettingsScreen(WIDTH, HEIGHT, settings)
        elif s == "leaderboard":
            current_screen = LeaderboardScreen(WIDTH, HEIGHT)
        elif s == "game":
            current_screen = GameSession(settings)
        elif s == "gameover":
            pass  

    build(state)

    running = True
    while running:
        clock.tick(FPS)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if state == "username":
            for event in events:
                result = current_screen.handle(event)
                if result == "done":
                    settings["username"] = current_screen.username
                    save_settings(settings)
                    state = "menu"
                    build(state)
            current_screen.draw(screen)

        elif state == "menu":
            for event in events:
                result = current_screen.handle(event)
                if result == "play":
                    state = "game"
                    build(state)
                elif result == "leaderboard":
                    state = "leaderboard"
                    build(state)
                elif result == "settings":
                    state = "settings"
                    build(state)
                elif result == "quit":
                    running = False
            current_screen.draw(screen)

        elif state == "settings":
            for event in events:
                result = current_screen.handle(event)
                if result == "back":
                    settings = current_screen.result_settings
                    save_settings(settings)
                    state = "menu"
                    build(state)
            current_screen.draw(screen)

        elif state == "leaderboard":
            for event in events:
                result = current_screen.handle(event)
                if result == "back":
                    state = "menu"
                    build(state)
            current_screen.draw(screen)

        elif state == "game":
            keys = pygame.key.get_pressed()
            current_screen.update(keys)
            current_screen.draw(screen)

            if current_screen.game_over:
                # Save score
                gs = current_screen
                add_score(
                    settings.get("username", "Player"),
                    gs.score, gs.distance, gs.coin_count,
                )
                # Build game-over screen
                state = "gameover"
                current_screen = GameOverScreen(
                    WIDTH, HEIGHT,
                    gs.score, gs.distance, gs.coin_count,
                    settings.get("username", "Player"),
                )


        elif state == "gameover":
            for event in events:
                result = current_screen.handle(event)
                if result == "retry":
                    state = "game"
                    build(state)
                elif result == "menu":
                    state = "menu"
                    build(state)
            current_screen.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()