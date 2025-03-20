import pygame
import json
import time

# Load steps.json
def load_steps(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Construction Site Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Load data
steps = load_steps("steps.json")
current_step = 0
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

def draw_text(text, x, y, color=BLACK):
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

# Main loop
running = True
while running:
    screen.fill(WHITE)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Display dynamic time
    if current_step < len(steps["schritte"]):
        time_value = steps["schritte"][current_step]["Time"]
        draw_text(f"Time: {time_value}", 850, 20, BLACK)
    
    # Draw Zentrum
    pygame.draw.rect(screen, BLUE, (50, 250, 120, 120), border_radius=10)
    draw_text("Zentrum", 70, 280)
    
    # Draw construction sites
    pygame.draw.rect(screen, RED, (300, 100, 120, 120), border_radius=10)
    draw_text("Baustelle A", 310, 130, WHITE)
    pygame.draw.rect(screen, RED, (500, 250, 120, 120), border_radius=10)
    draw_text("Baustelle B", 510, 280, WHITE)
    pygame.draw.rect(screen, RED, (300, 400, 120, 120), border_radius=10)
    draw_text("Baustelle C", 310, 430, WHITE)
    
    # Update display
    pygame.display.flip()
    clock.tick(2)
    
    # Move to the next step dynamically
    if current_step < len(steps["schritte"]) - 1:
        current_step += 1
    
pygame.quit()
