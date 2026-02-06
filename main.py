import pygame
import sys
import os
from settings import *

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

class KitchenScene(Scene):
    def draw(self, screen):
        screen.fill((50, 70, 90)) # A nice kitchen blue-grey
        self.game.draw_text("KITCHEN SCENE", 50, WIDTH // 2, HEIGHT // 2)
        self.game.draw_text("Press ESC to go home", 20, WIDTH // 2, HEIGHT - 50)

    def events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.start_transition("HOME")

# --- MAIN GAME ENGINE ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Assets Paths
        self.bg_path = os.path.join("assets", "images", "home_bg.png")
        self.logo_path = os.path.join("assets", "images", "logo.png")
        self.font_path = os.path.join("assets", "fonts", "LoveDays-2v7Oe.ttf")

        # Load Assets
        self.load_assets()

        # Button Setup
        self.start_btn_rect = pygame.Rect(0, 0, 200, 60)
        self.start_btn_rect.center = (WIDTH // 2, HEIGHT * 2 // 2.7)

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
            self.bg_img = pygame.image.load(self.bg_path).convert()
            self.bg_img = pygame.transform.smoothscale(self.bg_img, (WIDTH, HEIGHT))
        except: self.bg_img = None

    def draw_text(self, text, size, x, y, color=WHITE):
        try:
            font = pygame.font.Font(self.font_path, size) if self.font_path else pygame.font.SysFont("arial", size)
        except: font = pygame.font.SysFont("arial", size)
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, text_surf.get_rect(center=(x, y)))

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