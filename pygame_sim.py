import pygame
import sys
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Construction Site Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)

# Fonts
font = pygame.font.SysFont("Arial", 18)

# Constants for visualization
TRUCK_SIZE = 20
MACHINE_SIZE = 30
BAUSTELLE_SIZE = 100
WERK_SIZE = 50
ZENTRUM_SIZE = 100
MARGIN = 20
PROGRESS_BAR_HEIGHT = 10

# Positions for Baustellen, Werk, and Zentrum
BAUSTELLE_A_POS = (MARGIN, MARGIN)
BAUSTELLE_B_POS = (MARGIN, SCREEN_HEIGHT // 2)
BAUSTELLE_C_POS = (MARGIN, SCREEN_HEIGHT - MARGIN - BAUSTELLE_SIZE)
WERK_POS = (SCREEN_WIDTH - WERK_SIZE - MARGIN, SCREEN_HEIGHT // 2 - WERK_SIZE // 2)
ZENTRUM_POS = (SCREEN_WIDTH // 2 - ZENTRUM_SIZE // 2, SCREEN_HEIGHT - MARGIN - ZENTRUM_SIZE)

# Load truck and machine images (replace with actual images if available)
truck_img = pygame.Surface((TRUCK_SIZE, TRUCK_SIZE))
truck_img.fill(BLUE)
fraese_img = pygame.Surface((MACHINE_SIZE, MACHINE_SIZE))
fraese_img.fill(RED)
oberflaechen_img = pygame.Surface((MACHINE_SIZE, MACHINE_SIZE))
oberflaechen_img.fill(GREEN)
asphaltierer_img = pygame.Surface((MACHINE_SIZE, MACHINE_SIZE))
asphaltierer_img.fill(YELLOW)
walze_img = pygame.Surface((MACHINE_SIZE, MACHINE_SIZE))
walze_img.fill(GRAY)

# Function to draw Baustellen
def draw_baustellen():
    pygame.draw.rect(screen, BLACK, (*BAUSTELLE_A_POS, BAUSTELLE_SIZE, BAUSTELLE_SIZE), 2)
    pygame.draw.rect(screen, BLACK, (*BAUSTELLE_B_POS, BAUSTELLE_SIZE, BAUSTELLE_SIZE), 2)
    pygame.draw.rect(screen, BLACK, (*BAUSTELLE_C_POS, BAUSTELLE_SIZE, BAUSTELLE_SIZE), 2)
    screen.blit(font.render("Baustelle A", True, BLACK), (BAUSTELLE_A_POS[0], BAUSTELLE_A_POS[1] - 20))
    screen.blit(font.render("Baustelle B", True, BLACK), (BAUSTELLE_B_POS[0], BAUSTELLE_B_POS[1] - 20))
    screen.blit(font.render("Baustelle C", True, BLACK), (BAUSTELLE_C_POS[0], BAUSTELLE_C_POS[1] - 20))

# Function to draw Werk
def draw_werk():
    pygame.draw.rect(screen, BLACK, (*WERK_POS, WERK_SIZE, WERK_SIZE), 2)
    screen.blit(font.render("Werk", True, BLACK), (WERK_POS[0], WERK_POS[1] - 20))

# Function to draw Zentrum
def draw_zentrum():
    pygame.draw.rect(screen, BLACK, (*ZENTRUM_POS, ZENTRUM_SIZE, ZENTRUM_SIZE), 2)
    screen.blit(font.render("Zentrum", True, BLACK), (ZENTRUM_POS[0], ZENTRUM_POS[1] - 20))

# Function to draw progress bars for machines
def draw_progress_bar(x, y, width, progress):
    pygame.draw.rect(screen, BLACK, (x, y, width, PROGRESS_BAR_HEIGHT), 1)
    pygame.draw.rect(screen, GREEN, (x, y, width * progress, PROGRESS_BAR_HEIGHT))

# Function to get position based on location
def get_position(location):
    if location == "A":
        return BAUSTELLE_A_POS[0] + BAUSTELLE_SIZE // 2, BAUSTELLE_A_POS[1] + BAUSTELLE_SIZE // 2
    elif location == "B":
        return BAUSTELLE_B_POS[0] + BAUSTELLE_SIZE // 2, BAUSTELLE_B_POS[1] + BAUSTELLE_SIZE // 2
    elif location == "C":
        return BAUSTELLE_C_POS[0] + BAUSTELLE_SIZE // 2, BAUSTELLE_C_POS[1] + BAUSTELLE_SIZE // 2
    elif location == "w":
        return WERK_POS[0] + WERK_SIZE // 2, WERK_POS[1] + WERK_SIZE // 2
    elif location == "z":
        return ZENTRUM_POS[0] + ZENTRUM_SIZE // 2, ZENTRUM_POS[1] + ZENTRUM_SIZE // 2
    else:
        # Handle locations like "zA" (driving from z to A)
        if len(location) == 2:
            start = get_position(location[0])
            end = get_position(location[1])
            return start, end
        return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # Default position

# Function to draw machines and their progress bars
def draw_machines(machines):
    for machine in machines:
        pos = get_position(machine["location"])
        if isinstance(pos, tuple) and len(pos) == 2 and isinstance(pos[0], tuple):
            # If the machine is moving (e.g., "zA"), draw it at the starting point
            pos = pos[0]
        if machine["type"] == "Fraese":
            screen.blit(fraese_img, (pos[0] - MACHINE_SIZE // 2, pos[1] - MACHINE_SIZE // 2))
        elif machine["type"] == "Oberflaechen":
            screen.blit(oberflaechen_img, (pos[0] - MACHINE_SIZE // 2, pos[1] - MACHINE_SIZE // 2))
        elif machine["type"] == "Asphaltierer":
            screen.blit(asphaltierer_img, (pos[0] - MACHINE_SIZE // 2, pos[1] - MACHINE_SIZE // 2))
        elif machine["type"] == "Walze":
            screen.blit(walze_img, (pos[0] - MACHINE_SIZE // 2, pos[1] - MACHINE_SIZE // 2))

        # Draw progress bar
        if machine["activity"] == "Working":
            progress = (machine["endActivity"] - machine["startActivity"]) / 100  # Example progress calculation
            draw_progress_bar(pos[0] - MACHINE_SIZE // 2, pos[1] + MACHINE_SIZE // 2, MACHINE_SIZE, progress)

# Function to draw trucks and their movement
def draw_trucks(trucks):
    for truck in trucks:
        pos = get_position(truck["location"])
        if isinstance(pos, tuple) and len(pos) == 2 and isinstance(pos[0], tuple):
            # If the truck is moving (e.g., "zA"), draw it at the starting point and show the path
            start_pos, end_pos = pos
            pygame.draw.line(screen, ORANGE, start_pos, end_pos, 2)
            pos = start_pos
        screen.blit(truck_img, (pos[0] - TRUCK_SIZE // 2, pos[1] - TRUCK_SIZE // 2))

# Function to draw the current time
def draw_time(current_time):
    time_text = font.render(f"Time: {current_time} min", True, BLACK)
    screen.blit(time_text, (SCREEN_WIDTH - 200, MARGIN))

# Main function to run the visualization
def visualize_simulation(simulation_data):
    clock = pygame.time.Clock()
    current_step = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Clear the screen
        screen.fill(WHITE)

        # Draw Baustellen, Werk, and Zentrum
        draw_baustellen()
        draw_werk()
        draw_zentrum()

        # Get the current step data
        if current_step < len(simulation_data["schritte"]):
            step_data = simulation_data["schritte"][current_step]
            current_time = step_data["Time"]
            trucks = step_data["Laster"]
            machines = step_data["Maschinen"]

            # Draw trucks and machines
            draw_trucks(trucks)
            draw_machines(machines)

            # Draw the current time
            draw_time(current_time)

            # Move to the next step
            current_step += 1
        else:
            # Simulation finished
            screen.blit(font.render("Simulation Finished", True, BLACK), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        clock.tick(1)  # 1 step per second

# Load simulation data from steps.json
with open("steps.json", "r") as file:
    simulation_data = json.load(file)

# Run the visualization
visualize_simulation(simulation_data)