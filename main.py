import pygame
import sys
import os

# --- จัดการ PATH ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
def get_asset_path(relative_path):
    return os.path.join(CURRENT_DIR, relative_path)

# --- นำเข้าข้อมูล ---
try:
    from data.ingredients import INGREDIENT_DATA
    from data.recipes import FOOD_RECIPES, DRINK_RECIPES
except ImportError:
    print("can not download image")
    sys.exit()

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cooking Step-by-Step")
clock = pygame.time.Clock()

# --- COLORS & FONTS ---
WHITE, BLACK, GREEN, BLUE, RED = (255, 255, 255), (0, 0, 0), (46, 204, 113), (52, 152, 219), (231, 76, 60)
font_ui = pygame.font.SysFont("Tahoma", 22)
font_big = pygame.font.SysFont("Tahoma", 40, bold=True)

# --- LOAD IMAGES ---
def load_and_fix_image(rel_path, size):
    full_path = get_asset_path(rel_path)
    if os.path.exists(full_path):
        img = pygame.image.load(full_path).convert_alpha()
        return pygame.transform.scale(img, size)
    return pygame.Surface(size) # คืนค่าเป็นพื้นผิวว่างถ้าหาไม่เจอ

bg_start = load_and_fix_image(os.path.join("image", "firstpage", "index.png"), (WIDTH, HEIGHT))
img_fail = load_and_fix_image(os.path.join("image", "fail.png"), (250, 250))

# --- GAME STATE ---
# หน้า: 1 (START), 2 (FOOD), 3 (DRINK), 4 (RESULT)
scene = 1
food_bowl = set()
drink_bowl = set()
food_result = ""
drink_result = ""

# --- FUNCTIONS ---
def draw_btn(text, rect, color, hover_c):
    m_pos = pygame.mouse.get_pos()
    c = hover_c if rect.collidepoint(m_pos) else color
    pygame.draw.rect(screen, c, rect, border_radius=10)
    t = font_ui.render(text, True, WHITE)
    screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))

def get_recipe_name(bowl, recipe_dict):
    mix = frozenset(bowl)
    return recipe_dict.get(mix, "Failed (It's Ruined!)")

# --- MAIN LOOP ---
while True:
    screen.fill((240, 240, 240))
    
    # --- หน้าที่ 1: START ---
    if scene == 1:
        screen.blit(bg_start, (0, 0))
        btn_enter = pygame.Rect(400, 550, 200, 60)
        draw_btn("ENTER", btn_enter, GREEN, (39, 174, 96))

    # --- หน้าที่ 2: FOOD KITCHEN ---
    elif scene == 2:
        pygame.draw.rect(screen, GREEN, (0, 0, WIDTH, 60))
        screen.blit(font_ui.render("STEP 1: COOK YOUR FOOD", True, WHITE), (20, 15))
        
        ings = [n for n, i in INGREDIENT_DATA.items() if i["type"] == "food"]
        ing_btns = []
        for i, name in enumerate(ings):
            r, c = i // 6, i % 6
            rect = pygame.Rect(50 + (c * 155), 100 + (r * 60), 145, 50)
            draw_btn(name, rect, (127, 140, 141), (149, 165, 166))
            ing_btns.append((name, rect))

        pygame.draw.rect(screen, WHITE, (50, 450, 900, 80), border_radius=10)
        screen.blit(font_ui.render("Cooking: " + " + ".join(food_bowl), True, BLACK), (70, 475))
        
        btn_cook = pygame.Rect(400, 580, 200, 60)
        draw_btn("COOK", btn_cook, (39, 174, 96), (34, 153, 84))

    # --- หน้าที่ 3: DRINK CAFE ---
    elif scene == 3:
        pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, 60))
        screen.blit(font_ui.render("STEP 2: BREW YOUR DRINK", True, WHITE), (20, 15))
        
        ings = [n for n, i in INGREDIENT_DATA.items() if i["type"] == "drink"]
        ing_btns = []
        for i, name in enumerate(ings):
            r, c = i // 4, i % 4
            rect = pygame.Rect(150 + (c * 180), 150 + (r * 70), 160, 55)
            draw_btn(name, rect, (127, 140, 141), (149, 165, 166))
            ing_btns.append((name, rect))

        pygame.draw.rect(screen, WHITE, (50, 450, 900, 80), border_radius=10)
        screen.blit(font_ui.render("Brewing: " + " + ".join(drink_bowl), True, BLACK), (70, 475))

        btn_brew = pygame.Rect(400, 580, 200, 60)
        draw_btn("BREW", btn_brew, BLUE, (41, 128, 185))

    # --- หน้าที่ 4: FINAL RESULT ---
    elif scene == 4:
        screen.blit(font_big.render("--- YOUR MENU ---", True, BLACK), (WIDTH//2 - 150, 100))
        
        # แสดงผลอาหาร
        food_txt = f"Food: {food_result}"
        screen.blit(font_ui.render(food_txt, True, GREEN if "Failed" not in food_result else RED), (200, 250))
        if "Failed" in food_result: screen.blit(img_fail, (200, 300))

        # แสดงผลน้ำ
        drink_txt = f"Drink: {drink_result}"
        screen.blit(font_ui.render(drink_txt, True, BLUE if "Failed" not in drink_result else RED), (600, 250))
        if "Failed" in drink_result: screen.blit(img_fail, (600, 300))

        btn_restart = pygame.Rect(400, 600, 200, 60)
        draw_btn("PLAY AGAIN", btn_restart, (100, 100, 100), BLACK)

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            p = event.pos
            if scene == 1 and btn_enter.collidepoint(p): 
                scene = 2
            elif scene == 2:
                if btn_cook.collidepoint(p):
                    food_result = get_recipe_name(food_bowl, FOOD_RECIPES)
                    scene = 3
                for name, rect in ing_btns:
                    if rect.collidepoint(p): food_bowl.add(name)
            elif scene == 3:
                if btn_brew.collidepoint(p):
                    drink_result = get_recipe_name(drink_bowl, DRINK_RECIPES)
                    scene = 4
                for name, rect in ing_btns:
                    if rect.collidepoint(p): drink_bowl.add(name)
            elif scene == 4 and btn_restart.collidepoint(p):
                scene = 1; food_bowl.clear(); drink_bowl.clear()

    pygame.display.flip()
    clock.tick(60)