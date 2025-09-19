import pygame
import sys
import random

pygame.init()

RESOURCE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(RESOURCE_EVENT, 1000)  # samla resurser varje sekund


# --- KONSTANTER ---
TILE_SIZE = 80
GRID_SIZE = 5
UI_HEIGHT = 100
WIDTH = TILE_SIZE * GRID_SIZE + 300
HEIGHT = TILE_SIZE * GRID_SIZE + UI_HEIGHT

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
STONE_GRAY = (130, 130, 130)  # sten
BLUE = (0, 0, 255)            # vision
GREEN = (0, 200, 0)           # skog
BROWN = (184, 134, 11)        # vete
WATER_BLUE = (0, 150, 200)    # vatten
SCHOOL_RED = (200, 50, 50)    # skola
BUTTON_COLOR = (220, 220, 220)
BUTTON_HIGHLIGHT = (180, 180, 180)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The King's Vision – Byggmeny")

font = pygame.font.SysFont(None, 24)

# --- SPELDATA ---
grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
resources_science = 0
resources_stone = 0
resources_wood = 0
resources_wheat = 0
resources_iron = 0
resources_armor = 0

mine_positions = []
wood_positions = []
water_positions = []

# Placera max 2 sten-gruvor
while len(mine_positions) < 2:
    gx = random.randint(0, GRID_SIZE - 1)
    gy = random.randint(0, GRID_SIZE - 1)
    if (gx, gy) not in mine_positions:
        mine_positions.append((gx, gy))
        grid[gy][gx] = "mine"

# Placera max 2 skogar
while len(wood_positions) < 2:
    gx = random.randint(0, GRID_SIZE - 1)
    gy = random.randint(0, GRID_SIZE - 1)
    if (gx, gy) not in wood_positions and (gx, gy) not in mine_positions:
        wood_positions.append((gx, gy))
        grid[gy][gx] = "wood"

# Placera max 2 vatten
while len(water_positions) < 2:
    gx = random.randint(0, GRID_SIZE - 1)
    gy = random.randint(0, GRID_SIZE - 1)
    if (gx, gy) not in wood_positions and (gx, gy) not in mine_positions and (gx, gy) not in water_positions:
        water_positions.append((gx, gy))
        grid[gy][gx] = "water"

# King's Vision startposition
vision_x, vision_y = 0, 0

# Aktivt byggval
selected_build = None

show_build_menu = False

# Speltillstånd
game_state = "game"

# Research-träd
research_tree = [
    {"name": "Avancerad odling", "cost": {"wood": 20}, "unlocked": False},
    {"name": "Järn", "cost": {"Science": 10}, "unlocked": False},
    {"name": "Bibliotek", "cost": {"stone": 10, "wood": 10}, "unlocked": False},
    {"name": "Knights", "cost": {"stone": 20, "iron": 10}, "unlocked": False}
]

# --- FUNKTIONER ---
def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

            if grid[y][x] == "mine":
                pygame.draw.circle(screen, STONE_GRAY, rect.center, TILE_SIZE // 3)
            elif grid[y][x] == "wood":
                pygame.draw.circle(screen, GREEN, rect.center, TILE_SIZE // 3)
            elif grid[y][x] == "water":
                pygame.draw.circle(screen, WATER_BLUE, rect.center, TILE_SIZE // 3)
            elif grid[y][x] == "wheat":
                pygame.draw.circle(screen, BROWN, rect.center, TILE_SIZE // 3)
            elif grid[y][x] == "school":
                pygame.draw.rect(screen, SCHOOL_RED, rect.inflate(-20, -20))
            elif grid[y][x] == "smith":
                pygame.draw.rect(screen, (100, 100, 100), rect.inflate(-20, -20))
            elif grid[y][x] == "guild":
                pygame.draw.rect(screen, (150, 75, 0), rect.inflate(-20, -20))


            if (x, y) in get_vision_tiles():
                pygame.draw.rect(screen, BLUE, rect, 3)

def get_vision_tiles():
    tiles = [(vision_x, vision_y)]
    if vision_x + 1 < GRID_SIZE:
        tiles.append((vision_x + 1, vision_y))
    if vision_y + 1 < GRID_SIZE:
        tiles.append((vision_x, vision_y + 1))
    return tiles

def collect_resources():
    global resources_stone, resources_wood, resources_wheat, resources_iron, resources_armor, resources_science
    
    iron_reserached = any(t["name"] == "Järn" and t["unlocked"] for t in research_tree)

    for (x, y) in get_vision_tiles():
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            if grid[y][x] == "wood":
                resources_wood += 1
            elif grid[y][x] == "mine":
                resources_stone += 1
                if iron_reserached and random.random() < 0.5:
                    resources_iron += 1
            elif grid[y][x] == "school":
                resources_science += 10
            elif grid[y][x] == "wheat":
                resources_wheat += 1
            elif grid[y][x] == "smith":
                if resources_iron >= 4:
                    resources_iron -= 4
                    resources_armor += 1


def can_build_wheat(x, y):
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[ny][nx] == "water":
                    return True
    return False



def draw_ui():
    global show_build_menu
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - UI_HEIGHT, WIDTH, UI_HEIGHT))
    text = font.render(f"Science: {resources_science} | Sten: {resources_stone} | Trä: {resources_wood} | Vete: {resources_wheat} | Järn: {resources_iron} | Armor: {resources_armor}", True, BLACK)
    screen.blit(text, (10, HEIGHT - UI_HEIGHT + 10))

    buttons = []

    # Alltid synlig "Buildings"-knapp
    btn_buildings = pygame.Rect(10, HEIGHT - UI_HEIGHT + 40, 120, 40)
    pygame.draw.rect(screen, BUTTON_COLOR, btn_buildings)
    pygame.draw.rect(screen, BLACK, btn_buildings, 2)
    screen.blit(font.render("Buildings", True, BLACK), (btn_buildings.x + 10, btn_buildings.y + 10))
    buttons.append((btn_buildings, "toggle_menu"))

    if show_build_menu:

        start_x = 140
        spacing = 130

        # Rita dropdown under "Buildings"
        iron_unlocked = any(t["name"] == "Järn" and t["unlocked"] for t in research_tree)

        build_buttons = [
            ("Bygg odling", "wheat"),
            ("Bygg Skola", "school"),
            ("Bygg Guild", "guild")
        ]
        if iron_unlocked:
            build_buttons.append(("Bygg Smedja", "smith"))


        # Rita alternativen vertikalt
        for i, (label, build_type) in enumerate(build_buttons):
            rect = pygame.Rect(start_x + i * spacing, HEIGHT - UI_HEIGHT + 40, 120, 40)
            color = BUTTON_HIGHLIGHT if selected_build == build_type else BUTTON_COLOR
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            screen.blit(font.render(label, True, BLACK), (rect.x + 10, rect.y + 10))
            buttons.append((rect, build_type))

    return buttons



def draw_research_screen():
    screen.fill(WHITE)
    title = font.render("Forskningsmeny (tryck R för att stänga)", True, BLACK)
    screen.blit(title, (20, 20))

    y_offset = 60
    for tech in research_tree:
        status = "Upplåst" if tech["unlocked"] else "Lås upp"
        cost_text = ", ".join([f"{res}: {amt}" for res, amt in tech["cost"].items()])
        label = f"{tech['name']} ({cost_text}) - {status}"
        screen.blit(font.render(label, True, BLACK), (40, y_offset))
        y_offset += 30

def try_unlock_research(mx, my):
    global resources_science
    y_offset = 60
    for tech in research_tree:
        rect = pygame.Rect(40, y_offset, WIDTH - 80, 25)
        if rect.collidepoint(mx, my) and not tech["unlocked"]:
            cost = tech["cost"].get("science", 0)
            if resources_science >= cost:
                resources_science -= cost
                tech["unlocked"] = True
        y_offset += 30


# --- HUVUDLOOP ---
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == RESOURCE_EVENT: 
            if game_state == "game":
                    collect_resources()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if game_state == "research":
                try_unlock_research(mx, my)
            else:
                for rect, build_type in draw_ui():
                    if rect.collidepoint(mx, my):
                        if build_type == "toggle_menu":
                            show_build_menu = not show_build_menu
                        else:
                            selected_build = build_type
                        break
                else:
                    grid_x = mx // TILE_SIZE
                    grid_y = my // TILE_SIZE
                    if grid_y < GRID_SIZE and selected_build is not None:
                        if grid[grid_y][grid_x] is None:
                            if selected_build == "wheat" and resources_wood >= 10 and can_build_wheat(grid_x, grid_y):
                                grid[grid_y][grid_x] = "wheat"
                                resources_wood -= 10
                                selected_build = None

                            elif selected_build == "school" and resources_stone >= 10 and resources_wood >= 10:
                                grid[grid_y][grid_x] = "school"
                                resources_stone -= 10
                                resources_wood -= 10
                                selected_build = None
                            
                            elif selected_build == "smith" and resources_stone >= 15 and resources_wood >= 10:
                                grid[grid_y][grid_x] = "smith"
                                resources_stone -= 15
                                resources_wood -= 10
                                selected_build = None
                            
                            elif selected_build == "guild" and resources_stone >= 15 and resources_wood >= 15:
                                grid[grid_y][grid_x] = "guild"
                                resources_stone -= 15
                                resources_wood -= 15
                                selected_build = None


        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_LEFT:
                vision_x = max(0, vision_x - 1)
            elif event.key == pygame.K_RIGHT:
                vision_x = min(GRID_SIZE - 1, vision_x + 1)
            elif event.key == pygame.K_UP:
                vision_y = max(0, vision_y - 1)
            elif event.key == pygame.K_DOWN:
                vision_y = min(GRID_SIZE - 1, vision_y + 1)


    if game_state == "game":
        draw_grid()
        buttons = draw_ui()
    else:
        draw_research_screen()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
