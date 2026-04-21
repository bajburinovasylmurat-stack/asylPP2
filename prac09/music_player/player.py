import pygame

class MusicPlayer:

    def __init__(self):

        pygame.mixer.init()

        self.tracks = [
            "music/track1.wav",
            "music/track2.wav"
        ]

        self.index = 0

        self.font = pygame.font.SysFont(None, 36)

    def play(self):

        pygame.mixer.music.load(
            self.tracks[self.index]
        )

        pygame.mixer.music.play()

    def stop(self):

        pygame.mixer.music.stop()

    def next(self):

        self.index += 1

        if self.index >= len(self.tracks):
            self.index = 0

        self.play()

    def previous(self):

        self.index -= 1

        if self.index < 0:
            self.index = len(self.tracks) - 1

        self.play()

    def draw(self, screen):

        text = self.font.render(
            f"Track: {self.index + 1}",
            True,
            (255, 255, 255)
        )

        screen.blit(text, (150, 130))