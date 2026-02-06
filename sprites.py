import pygame
import os
from settings import *

class Pot(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        
        # Load Pot Body
        self.image = pygame.image.load(os.path.join("assets", "images", "pot.png")).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (300, 300))
        self.is_cooking = False 
        self.cook_start_time = 0
        self.cook_duration = 3000 # 3 seconds
        
        # Load Pot Lid
        try:
            self.lid_image = pygame.image.load(os.path.join("assets", "images", "pot_lid.png")).convert_alpha()
            self.lid_image = pygame.transform.smoothscale(self.lid_image, (300, 300))
        except:
            self.lid_image = None # Fallback if lid missing

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        # Check if 3 seconds have passed
        if self.is_cooking:
            now = pygame.time.get_ticks()
            if now - self.cook_start_time > self.cook_duration:
                self.is_cooking = False # Open the lid!

    def start_cooking(self):
        self.is_cooking = True
        self.cook_start_time = pygame.time.get_ticks()

class Ingredient(pygame.sprite.Sprite):
    def __init__(self, game, name, x, y):
        super().__init__()
        self.game = game
        self.name = name
        self.start_pos = (x, y)
        
        # Load the image based on the name passed in
        image_path = os.path.join("assets", "images", f"{name}.png")
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, (80, 80))
        except:
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 200, 0)) # Yellow placeholder
            
        self.rect = self.image.get_rect(center=self.start_pos)
        self.is_added = False  # Track if it's "in" the pot
        self.visible = True    # Track if we should draw it

    def reset(self):
        self.is_added = False
        self.visible = True
        self.rect.center = self.start_pos