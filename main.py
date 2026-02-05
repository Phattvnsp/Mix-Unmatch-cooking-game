import pygame
import sys
import os
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # --- LOAD LOGO ---
        self.logo_path = os.path.join("assets", "images", "logo.png")
        
        try:
            self.logo_img = pygame.image.load(self.logo_path).convert_alpha()
            self.logo_img = pygame.transform.smoothscale(self.logo_img, (450, 300))
            self.logo_rect = self.logo_img.get_rect()
            
            # POSITION: Top-ish and Center
            # WIDTH // 2 keeps it centered, HEIGHT // 3 moves it up to the top third
            self.logo_rect.center = (WIDTH // 2, HEIGHT // 3)
            
        except:
            print("Logo not found! Using placeholder.")
            self.logo_img = pygame.Surface((450, 300))
            self.logo_img.fill((255, 0, 255))
            self.logo_rect = self.logo_img.get_rect()
            self.logo_rect.center = (WIDTH // 2, HEIGHT // 3)

        # --- BUTTON SETUP ---
        self.btn_width, self.btn_height = 200, 60
        self.start_btn_rect = pygame.Rect(0, 0, self.btn_width, self.btn_height)
        # Position button in the bottom third
        self.start_btn_rect.center = (WIDTH // 2, HEIGHT * 2 // 3)

    def draw_text(self, text, size, x, y, color=WHITE):
        font = pygame.font.SysFont("arial", size, bold=True)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def show_homepage(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            
            # 1. Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if the mouse clicked the button area
                    if self.start_btn_rect.collidepoint(mouse_pos):
                        waiting = False
            
            # 2. Drawing
            self.screen.fill(BG_COLOR)
            
            # Draw Logo
            self.screen.blit(self.logo_img, self.logo_rect)
            
            # Draw Button logic (Hover effect)
            button_color = (150, 255, 150)
            if self.start_btn_rect.collidepoint(mouse_pos):
                button_color = (112, 130, 62)
            
            # Draw the button rectangle
            pygame.draw.rect(self.screen, button_color, self.start_btn_rect, border_radius=12)
            # Draw the text on top of the button
            self.draw_text("START GAME", 24, self.start_btn_rect.centerx, self.start_btn_rect.centery, color=(0, 50, 0))
            
            pygame.display.flip()

if __name__ == "__main__":
    g = Game()
    g.show_homepage()
    print("Transitioning to the Kitchen...")
    # This is where you'd call g.run() or your main game loop