import pygame
import sys
import os
from settings import *
from sprites import *
import math
from data.recipes import FOOD_RECIPES, DRINK_RECIPES

# --- SCENE CLASSES ---

class Scene:
    def __init__(self, game):
        self.game = game
    def events(self, events): pass
    def update(self): pass
    def draw(self, screen): pass

class HomeScene(Scene):
    def events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            # Start with Click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game.start_btn_rect.collidepoint(mouse_pos):
                    self.game.start_transition("KITCHEN")
            # Start with Enter Key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.start_transition("KITCHEN")

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        # 1. Background
        if self.game.bg_img:
            screen.blit(self.game.bg_img, (0, 0))
        else:
            screen.fill(BG_COLOR)
        
        # 2. Logo
        screen.blit(self.game.logo_img, self.game.logo_rect)
        
        # 3. Button
        button_color = (253, 219, 83)
        if self.game.start_btn_rect.collidepoint(mouse_pos):
            button_color = (238, 192, 92)
            
        pygame.draw.rect(screen, button_color, self.game.start_btn_rect, border_radius=12)
        self.game.draw_text("START GAME", 24, self.game.start_btn_rect.centerx, self.game.start_btn_rect.centery, color=(0, 50, 0))
        self.game.draw_text("Or press Enter to start", 20, WIDTH // 2, HEIGHT - 50 , color=(0, 50, 0))

class KitchenScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.entry_time = pygame.time.get_ticks()
        self.display_duration = 1000
        
        # 1. Setup the Pot
        self.pot = Pot(game, WIDTH // 2, HEIGHT // 2 - 10)
        
        # 2. Setup Ingredients Group
        self.ingredients = pygame.sprite.Group()
        
        # --- THE SMART SPAWN LOOP ---
        
        # A list of everything you want on the shelf right now
        # Make sure you have .png images for all of these!
        shelf_list = [
            "Egg"
        ]
        
        # Grid Settings
        start_x = 80      # Where the first item starts (Left)
        start_y = 45     # Where the first row starts (Top)
        gap_x = 90        # Horizontal space between items
        gap_y = 90        # Vertical space between rows
        cols = 6          # How many items before starting a new row
        
        for i, item_name in enumerate(shelf_list):
            # Math to calculate row and column
            col = i % cols              # 0, 1, 2, 3, 4, 5, 0, 1...
            row = i // cols             # 0, 0, 0, 0, 0, 0, 1, 1...
            
            x = start_x + (col * gap_x)
            y = start_y + (row * gap_y)
            
            # Create the ingredient and add to group
            new_item = Ingredient(self.game, item_name, x, y)
            self.ingredients.add(new_item)

        self.showing_result = False
        self.result_start_time = 0
        self.result_duration = 3000 # Show result for 3 seconds
        self.current_dish_name = ""
        self.current_dish_image = None

    def draw(self, screen):
        self.mouse_pos = pygame.mouse.get_pos()
        
        # 1. Draw Background & Pot
        if self.game.kitchen_bg_img: screen.blit(self.game.kitchen_bg_img, (0, 0))
        else: screen.fill(BG_COLOR)
        
        # Logic to detect when cooking JUST finished
        was_cooking = self.pot.is_cooking
        self.pot.update()
        
        # 2. Draw Pot Body
        screen.blit(self.pot.image, self.pot.rect)

        # 3. IF COOKING FINISHED: Trigger the Result Screen
        if was_cooking and not self.pot.is_cooking:
            self.trigger_result_screen()

        # 4. Draw Ingredients (Hidden if cooking or showing result)
        if not self.showing_result: 
            # Only draw ingredients if we are NOT showing the result screen
            for item in self.ingredients:
                if item.visible:
                    screen.blit(item.image, item.rect)

        # 5. COOKING ANIMATION (Lid + Pulsing Text)
        if self.pot.is_cooking:
            lid_pos = self.pot.rect.x, self.pot.rect.y
            if self.pot.lid_image: screen.blit(self.pot.lid_image, lid_pos)
            
            # Dark Overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(160)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Pulsing Text
            pulse_val = 155 + int(100 * math.sin(pygame.time.get_ticks() * 0.005))
            self.game.draw_text("Cooking...", 80, WIDTH // 2, HEIGHT // 2, color=WHITE, alpha=pulse_val)

        # 6. --- THE NEW RESULT SCREEN ---
        if self.showing_result:
            self.draw_result(screen)

        # 7. UI Elements (Buttons/Text) - Only show if NOT showing result
        if not self.showing_result:
            self.draw_ui(screen)
    def get_added_ingredients_text(self):
        # Get names of all items where is_added is True
        added_names = [item.name for item in self.ingredients if item.is_added]
        
        if not added_names:
            return "empty"
        
        # Joins them with commas (e.g., "Egg, Milk, Flour")
        return ", ".join(added_names)

    def draw_ui(self, screen):
        # Cafe Button
        button_color = (159, 129, 112)
        if self.game.cafe_btn_rect.collidepoint(self.mouse_pos): button_color = (111, 78, 55)
        pygame.draw.rect(screen, button_color, self.game.cafe_btn_rect, border_radius=8)
        self.game.draw_text("CAFE", 24, self.game.cafe_btn_rect.centerx, self.game.cafe_btn_rect.centery)
        self.game.draw_text("Add ingredients then tap the pot!", 20, WIDTH // 2, HEIGHT - 50 , color=NAVY)
        
        # "KITCHEN" Entry Text
        if pygame.time.get_ticks() - self.entry_time < self.display_duration:
            self.game.draw_text("KITCHEN", 65, WIDTH // 2, HEIGHT // 7, color=NAVY)
        
        ingredients_list = self.get_added_ingredients_text()
        # 2. Draw the text under the pot
        self.game.draw_text(
            f"In Pot: {ingredients_list}", 
            22, 
            WIDTH // 2, 
            HEIGHT // 2 + 140, 
            color=NAVY)

    def trigger_result_screen(self):
        # 1. Calculate what we made
        self.current_dish_name = self.check_recipe()
        
        # 2. Add to unlocked menu
        self.game.unlocked_dishes.add(self.current_dish_name)
        
        # 3. Decide which image to show
        # Try to load an image named "Pad Thai.png", otherwise use "meme.png"
        try:
            path = os.path.join("assets", "images", f"{self.current_dish_name}.png")
            img = pygame.image.load(path).convert_alpha()
            self.current_dish_image = pygame.transform.smoothscale(img, (200, 200))
        except:
            # If image not found (or it's Mystery/Failed), use the MEME!
            self.current_dish_image = self.game.meme_img

        # 4. Start the timer
        self.showing_result = True
        self.result_start_time = pygame.time.get_ticks()

    def draw_result(self, screen):
        # 1. Dim Background
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200) # Darker than cooking
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 2. Draw Shiny Effect
        shiny_rect = self.game.shiny_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(self.game.shiny_img, shiny_rect)

        # 3. Draw The Dish Image
        if self.current_dish_image:
            dish_rect = self.current_dish_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(self.current_dish_image, dish_rect)

        # 4. Draw The Name
        self.game.draw_text("YOU MADE:", 30, WIDTH // 2, HEIGHT // 2 + 80, color=WHITE)
        self.game.draw_text(self.current_dish_name, 50, WIDTH // 2, HEIGHT // 2 + 130, color=(255, 255, 255)) # White text

        # 5. Check Timer to Close
        if pygame.time.get_ticks() - self.result_start_time > self.result_duration:
            self.showing_result = False
            # NOW we reset the ingredients
            for item in self.ingredients:
                item.reset()

    def events(self, events):
        self.mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.start_transition("HOME")
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    
                    # 1. Check Ingredient Clicks (Only if NOT cooking)
                    if not self.pot.is_cooking:
                        for item in self.ingredients:
                            # Only check visible items
                            if item.visible and item.rect.collidepoint(self.mouse_pos):
                                print(f"Added {item.name} to the pot!")
                                item.is_added = True
                                item.visible = False
                    
                    # 2. Check Pot Click
                    if self.pot.rect.collidepoint(self.mouse_pos):
                        has_food = any(item.is_added for item in self.ingredients)
                        if not self.pot.is_cooking:
                            if has_food:
                                self.pot.start_cooking()
                                print(f"Cooking ... {[item.name for item in self.ingredients if item.is_added]}")
                            else:
                                print("Pot is empty!")
                        else:
                            print("Already cooking!")

                    # 3. Check Cafe Button
                    if self.game.cafe_btn_rect.collidepoint(self.mouse_pos):
                        print("Cafe button clicked!")

    def check_recipe(self):
        # 1. Collect names of ingredients added (using Title case to match your dict)
        in_pot = frozenset([item.name.capitalize() for item in self.ingredients if item.is_added])
        # 2. Look for matches in both dictionaries
        # .get() is great because it returns None if there's no match instead of crashing
        result = FOOD_RECIPES.get(in_pot) or DRINK_RECIPES.get(in_pot)
        if result:
            print(f"Result: {result}")
            return result
        else:
            print("No matching recipe found.")
            return "Failed Dish"

class CafeScene(Scene):
    def __init__(self, game):
        super().__init__(game)
    def draw(self, screen):
        screen.fill(BG_COLOR)
        self.game.draw_text("CAFE SCENE - Coming Soon!", 40, WIDTH // 2, HEIGHT // 2, color=NAVY)

    def events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.start_transition("KITCHEN")


# --- MAIN GAME ENGINE ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Assets Paths
        self.homebg_path = os.path.join("assets", "images", "home_bg.png")
        self.logo_path = os.path.join("assets", "images", "logo.png")
        self.font_path = os.path.join("assets", "fonts", "LoveDays-2v7Oe.ttf")
        self.kitchenbg_path = os.path.join("assets", "images", "kitchen_bg.png")

        self.unlocked_dishes = set()
        # Load Assets
        self.load_assets()

        # Button Setup
        self.start_btn_rect = pygame.Rect(0, 0, 200, 60)
        self.start_btn_rect.center = (WIDTH // 2, HEIGHT * 2 // 2.7)
        self.cafe_btn_rect = pygame.Rect(0, 0, 60, 50)
        self.cafe_btn_rect.midright = (WIDTH - 20, HEIGHT // 2)

        # State & Transition Setup
        self.scene = HomeScene(self)
        self.state = "NORMAL" # NORMAL or TRANSITIONING
        self.next_state_name = ""
        self.fade_alpha = 0
        self.fade_surf = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surf.fill((0, 0, 0))

    def load_assets(self):
        # Font
        if not os.path.isfile(self.font_path): self.font_path = None
        # Logo
        try:
            self.logo_img = pygame.image.load(self.logo_path).convert_alpha()
            self.logo_img = pygame.transform.smoothscale(self.logo_img, (450, 300))
            self.logo_rect = self.logo_img.get_rect(center=(WIDTH // 2, HEIGHT // 2.5))
        except:
            self.logo_img = pygame.Surface((450, 300)); self.logo_img.fill((255, 0, 255))
            self.logo_rect = self.logo_img.get_rect(center=(WIDTH // 2, HEIGHT // 2.5))
        # BG
        try:
            self.bg_img = pygame.image.load(self.homebg_path).convert()
            self.bg_img = pygame.transform.smoothscale(self.bg_img, (WIDTH, HEIGHT))
        except: self.bg_img = None
        try:
            self.kitchen_bg_img = pygame.image.load(self.kitchenbg_path).convert()
            self.kitchen_bg_img = pygame.transform.smoothscale(self.kitchen_bg_img, (WIDTH, HEIGHT))
        except: self.kitchen_bg_img = None
        try:
            self.shiny_img = pygame.image.load(os.path.join("assets", "images", "shiny.png")).convert_alpha()
            # Make it big!
            self.shiny_img = pygame.transform.smoothscale(self.shiny_img, (600, 600)) 
        except:
            self.shiny_img = pygame.Surface((400, 400)) # Fallback
            self.shiny_img.fill((255, 255, 0))
            self.shiny_img.set_alpha(100)

        try:
            self.meme_img = pygame.image.load(os.path.join("assets", "images", "meme.png")).convert_alpha()
            self.meme_img = pygame.transform.smoothscale(self.meme_img, (200, 200))
        except:
            self.meme_img = pygame.Surface((200, 200))
            self.meme_img.fill((100, 100, 100))

    def draw_text(self, text, size, x, y, color=WHITE, alpha=255):
        try:
            font = pygame.font.Font(self.font_path, size) if self.font_path else pygame.font.SysFont("arial", size)
        except: font = pygame.font.SysFont("arial", size)
        text_surf = font.render(text, True, color)
        text_surf.set_alpha(alpha)
        text_rect = text_surf.get_rect(center=(x, y))
        self.screen.blit(text_surf, text_rect)

    def start_transition(self, next_scene_name):
        self.state = "TRANSITIONING"
        self.next_state_name = next_scene_name
        self.fade_alpha = 0

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
            
            # 1. Update Transition
            if self.state == "TRANSITIONING":
                self.fade_alpha += 7 # Speed of fade
                if self.fade_alpha >= 255:
                    # Switch the scene for real once it's fully black
                    if self.next_state_name == "KITCHEN": self.scene = KitchenScene(self)
                    if self.next_state_name == "HOME": self.scene = HomeScene(self)
                    self.state = "NORMAL"
                    self.fade_alpha = 0

            # 2. Scene Logic
            if self.state == "NORMAL":
                self.scene.events(events)
            
            # 3. Draw
            self.scene.draw(self.screen)
            
            # 4. Draw Fade Overlay
            if self.state == "TRANSITIONING" or self.fade_alpha > 0:
                self.fade_surf.set_alpha(self.fade_alpha)
                self.screen.blit(self.fade_surf, (0, 0))
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    g = Game()
    g.run()