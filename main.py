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
        # Make sure your logo is in assets/images/logo.png
        self.logo_path = os.path.join("assets", "images", "logo.png")
        
        try:
            self.logo_img = pygame.image.load(self.logo_path).convert_alpha()
            
            # 1. DEFINE YOUR DESIRED SIZE
            # (Try 300x300 or whatever fits your vision)
            desired_size = (300, 300) 
            
            # 2. RESIZE THE IMAGE
            # smoothscale makes it look better than regular 'scale'
            self.logo_img = pygame.transform.smoothscale(self.logo_img, desired_size)
            
            # 3. NOW CENTER THE RECT
            self.logo_rect = self.logo_img.get_rect()
            self.logo_rect.center = (WIDTH // 2, HEIGHT // 2)
        except:
            print("Logo not found! Creating a placeholder box instead.")
            self.logo_img = pygame.Surface((300, 300))
            self.logo_img.fill((255, 0, 255)) # Pink box
            self.logo_rect = self.logo_img.get_rect()
            self.logo_rect.center = (WIDTH // 2, HEIGHT // 2)

    def draw_text(self, text, size, x, y):
        font = pygame.font.SysFont("arial", size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def show_homepage(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            
            # 1. Events (Checking for exit)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False # Press any key to "start"
            
            # 2. Drawing
            self.screen.fill(BG_COLOR)
            
            # Draw the logo centered
            self.screen.blit(self.logo_img, self.logo_rect)
            
            # Draw some instructions
            self.draw_text("MIX-UNMATCH COOKING", 40, WIDTH // 2, HEIGHT // 2 + 150)
            self.draw_text("Press any key to start", 20, WIDTH // 2, HEIGHT - 50)
            
            pygame.display.flip()

if __name__ == "__main__":
    g = Game()
    g.show_homepage()
    print("Game starts now!")
    pygame.quit()