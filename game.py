import pygame
import random

# Konstanten
WIDTH, HEIGHT = 800, 600
FPS = 30

# Farben
WHITE = (255, 255, 255)
GREEN = (34, 177, 76)
GRAY = (169, 169, 169)
YELLOW = (255, 215, 0)

# Initialisiere Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Baustellen-Klassen
class Baustelle:
    PHASEN = ["Fräsen", "Oberflächenbearbeitung", "Asphaltieren", "Walzen"]
    LEISTUNG = {"Fräsen": 50, "Oberflächenbearbeitung": 21, "Asphaltieren": 30, "Walzen": 48}
    
    def __init__(self, x, y, masse):
        self.x = x
        self.y = y
        self.masse = masse  # Gesamtmasse in Tonnen
        self.phase_index = 0
        self.fortschritt = 0
    
    def update(self):
        if self.phase_index < len(self.PHASEN):
            phase = self.PHASEN[self.phase_index]
            self.fortschritt += self.LEISTUNG[phase] / FPS
            if self.fortschritt >= self.masse:
                self.fortschritt = 0
                self.phase_index += 1
    
    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), 20)
        pygame.draw.rect(screen, YELLOW, (self.x - 20, self.y + 25, 40, 5))
        pygame.draw.rect(screen, GRAY, (self.x - 20, self.y + 25, int(40 * (self.fortschritt / self.masse)), 5))

# Spiel-Setup
baustellen = [Baustelle(random.randint(100, 700), random.randint(100, 500), random.randint(200, 500)) for _ in range(3)]

running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    for baustelle in baustellen:
        baustelle.update()
        baustelle.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
