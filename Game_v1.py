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
STONE_GRAY = (130, 130, 130)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
BROWN = (184, 134, 11)
WATER_BLUE = (0, 150, 200)
SCHOOL_RED = (200, 50, 50)
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

army_spearmen = 0
army_knights = 0

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

vision_x, vision_y = 0, 0
selected_build = None
show_build_menu = False
show_recruit_menu = False
show_research_menu = False  # FIX: ny variabel för research

game_state = "game"

wave_number = 0
max_waves = 10
game_over = False
victory = False

time_to_next_wave = 60  # FIX: nedräkningstid

# Research-träd
research_tree = [
    {"name": "Avancerad odling", "cost": {"wood": 20}, "unlocked": False},
    {"name": "Järn", "cost": {"science": 10}, "unlocked": False},
    {"name": "Bibliotek", "cost": {"stone": 10, "wood": 10}, "unlocked": False},
    {"name": "Knights", "cost": {"stone": 20, "iron": 10}, "unlocked": False}
]

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
    global show_build_menu, show_recruit_menu, show_research_menu
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - UI_HEIGHT, WIDTH, UI_HEIGHT))
    text = font.render(
        f"Science: {resources_science} | Sten: {resources_stone} | Trä: {resources_wood} | Vete: {resources_wheat} | Järn: {resources_iron} | Armor: {resources_armor} | Spearmen: {army_spearmen} | Knights: {army_knights}", 
        True, BLACK)
    screen.blit(text, (10, HEIGHT - UI_HEIGHT + 10))
    screen.blit(font.render(f"Nästa våg om: {time_to_next_wave}s", True, BLACK), (WIDTH - 200, 50))

    buttons = []
    btn_buildings = pygame.Rect(10, HEIGHT - UI_HEIGHT + 40, 120, 40)
    pygame.draw.rect(screen, BUTTON_COLOR, btn_buildings)
    pygame.draw.rect(screen, BLACK, btn_buildings, 2)
    screen.blit(font.render("Buildings", True, BLACK), (btn_buildings.x + 10, btn_buildings.y + 10))
    buttons.append((btn_buildings, "toggle_menu"))

    btn_research = pygame.Rect(270, HEIGHT - UI_HEIGHT + 40, 120, 40)
    pygame.draw.rect(screen, BUTTON_COLOR, btn_research)
    pygame.draw.rect(screen, BLACK, btn_research, 2)
    screen.blit(font.render("Research", True, BLACK), (btn_research.x + 10, btn_research.y + 10))
    buttons.append((btn_research, "toggle_research"))

    if any("guild" in row for row in grid):
        btn_recruit = pygame.Rect(140, HEIGHT - UI_HEIGHT + 40, 120, 40)
        pygame.draw.rect(screen, BUTTON_COLOR, btn_recruit)
        pygame.draw.rect(screen, BLACK, btn_recruit, 2)
        screen.blit(font.render("Recruitment", True, BLACK), (btn_recruit.x + 5, btn_recruit.y + 10))
        buttons.append((btn_recruit, "toggle_recruit"))

    if show_build_menu:
        start_x = 300
        spacing = 130
        iron_unlocked = any(t["name"] == "Järn" and t["unlocked"] for t in research_tree)
        build_buttons = [("Bygg odling", "wheat"), ("Bygg Skola", "school"), ("Bygg Guild", "guild")]
        if iron_unlocked:
            build_buttons.append(("Bygg Smedja", "smith"))
        for i, (label, build_type) in enumerate(build_buttons):
            rect = pygame.Rect(start_x + i * spacing, HEIGHT - UI_HEIGHT + 40, 120, 40)
            color = BUTTON_HIGHLIGHT if selected_build == build_type else BUTTON_COLOR
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            screen.blit(font.render(label, True, BLACK), (rect.x + 10, rect.y + 10))
            buttons.append((rect, build_type))

    if show_recruit_menu:
        start_x = 300
        spacing = 130
        recruit_buttons = [("Träna Spearman (10 vete)", "spearman")]
        if any(t["name"] == "Knights" and t["unlocked"] for t in research_tree):
            recruit_buttons.append(("Träna Knight (1 armor)", "knight"))
        for i, (label, recruit_type) in enumerate(recruit_buttons):
            rect = pygame.Rect(start_x + i * spacing, HEIGHT - UI_HEIGHT + 40, 180, 40)
            pygame.draw.rect(screen, BUTTON_COLOR, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            screen.blit(font.render(label, True, BLACK), (rect.x + 5, rect.y + 10))
            buttons.append((rect, recruit_type))

    if show_research_menu:
        start_x = 450
        for i, tech in enumerate(research_tree):
            status = "✔" if tech["unlocked"] else f"Kostnad: {tech['cost']}"
            rect = pygame.Rect(start_x, HEIGHT - UI_HEIGHT + 40 + i * 45, 180, 40)
            pygame.draw.rect(screen, BUTTON_COLOR, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            screen.blit(font.render(f"{tech['name']} ({status})", True, BLACK), (rect.x + 5, rect.y + 10))
            buttons.append((rect, f"research_{i}"))

    return buttons

def spawn_wave():   
    global wave_number, game_over, victory
    if wave_number >= max_waves:
        victory = True
        return
    wave_number += 1
    enemy_strength = 5 + wave_number * 2
    player_strength = army_spearmen * 2 + army_knights * 5
    if player_strength < enemy_strength:
        game_over = True

# --- HUVUDLOOP ---
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == RESOURCE_EVENT:
            if game_state == "game" and not game_over and not victory:
                collect_resources()
                time_to_next_wave -= 1
                if time_to_next_wave <= 0:
                    spawn_wave()
                    time_to_next_wave = 60
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if game_state == "game" and not game_over and not victory:
                for rect, action in draw_ui():
                    if rect.collidepoint(mx, my):
                        if action == "toggle_menu":
                            show_build_menu = not show_build_menu
                            show_recruit_menu = False
                            show_research_menu = False
                        elif action == "toggle_recruit":
                            show_recruit_menu = not show_recruit_menu
                            show_build_menu = False
                            show_research_menu = False
                        elif action == "toggle_research":
                            show_research_menu = not show_research_menu
                            show_build_menu = False
                            show_recruit_menu = False
                        elif action.startswith("research_"):
                            idx = int(action.split("_")[1])
                            tech = research_tree[idx]
                            if not tech["unlocked"]:
                                cost_ok = True
                                for res, cost in tech["cost"].items():
                                    if globals()[f"resources_{res}"] < cost:
                                        cost_ok = False
                                        break
                                if cost_ok:
                                    for res, cost in tech["cost"].items():
                                        globals()[f"resources_{res}"] -= cost
                                    tech["unlocked"] = True
                        elif action == "spearman" and resources_wheat >= 10:
                            army_spearmen += 1
                            resources_wheat -= 10
                        elif action == "knight" and resources_armor >= 1:
                            army_knights += 1
                            resources_armor -= 1
                        else:
                            selected_build = action
                        break
                else:
                    grid_x = mx // TILE_SIZE
                    grid_y = my // TILE_SIZE
                    if grid_y < GRID_SIZE and selected_build is not None:
                        if grid[grid_y][grid_x] is None:
                            if selected_build == "wheat" and resources_wood >= 10 and can_build_wheat(grid_x, grid_y):
                                grid[grid_y][grid_x] = "wheat"
                                resources_wood -= 10
                            elif selected_build == "school" and resources_stone >= 10 and resources_wood >= 10:
                                grid[grid_y][grid_x] = "school"
                                resources_stone -= 10
                                resources_wood -= 10
                            elif selected_build == "smith" and resources_stone >= 15 and resources_wood >= 10:
                                grid[grid_y][grid_x] = "smith"
                                resources_stone -= 15
                                resources_wood -= 10
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
        if game_over:
            screen.blit(font.render("GAME OVER - Fienden besegrade dig!", True, (255, 0, 0)), (200, 200))
        elif victory:
            screen.blit(font.render("VICTORY - Du överlevde alla vågor!", True, (0, 200, 0)), (200, 200))
        else:
            screen.blit(font.render(f"Wave: {wave_number}/{max_waves}", True, BLACK), (WIDTH - 150, 20))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
